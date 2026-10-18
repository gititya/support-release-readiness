/* Runs in macOS system JavaScript. No model calls, network or package imports. */
var FS, home, mkdirNative, processAlive, processID, nativeOpen, nativeFlock, nativeClose, nativeRename;

function fail(message) { throw new Error(message); }
function check(value, message) { if (!value) fail(message); }
function own(obj, key) { return Object.prototype.hasOwnProperty.call(obj, key); }
function copy(value) { return JSON.parse(JSON.stringify(value)); }
function object(value) { return value && typeof value === 'object' && !Array.isArray(value); }
function text(value, name) { check(typeof value === 'string' && value.trim().length > 0, name + ' is required'); return value; }
function id(value) {
    check(typeof value === 'string' && /^[a-z0-9][a-z0-9-]{0,63}$/.test(value) &&
        ['constructor', 'prototype'].indexOf(value) < 0, 'Use a short ID with lowercase letters, numbers and hyphens');
    return value;
}
function safeObject(value) {
    if (!value || typeof value !== 'object') return;
    Object.keys(value).forEach(function (key) {
        check(['__proto__', 'prototype', 'constructor'].indexOf(key) < 0, 'Unsafe object key');
        safeObject(value[key]);
    });
}
function number(value, name) { check(typeof value === 'number' && isFinite(value) && value >= 0, name + ' must be a nonnegative finite number'); return value; }
function instant(value) {
    check(typeof value === 'string' && /^\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d(?:\.\d+)?)?(Z|[+-]\d\d:\d\d)$/.test(value), 'Timestamp needs a date, time and explicit UTC offset');
    var dateParts = value.slice(0, 10).split('-').map(Number), year = dateParts[0], month = dateParts[1], day = dateParts[2];
    var days = [31, (year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    check(month >= 1 && month <= 12 && day >= 1 && day <= days[month - 1], 'Invalid calendar date');
    var result = new Date(value); check(isFinite(result.getTime()), 'Invalid timestamp'); return result;
}
function sha256(value) {
    var bytes = unescape(encodeURIComponent(value)), words = [], bits = bytes.length * 8;
    var k = [], h = [], n = 2, i, j, composite;
    while (k.length < 64) {
        composite = false;
        for (j = 2; j * j <= n; j++) if (n % j === 0) { composite = true; break; }
        if (!composite) {
            if (h.length < 8) h.push((Math.sqrt(n) * 4294967296) | 0);
            k.push((Math.pow(n, 1 / 3) * 4294967296) | 0);
        }
        n++;
    }
    for (i = 0; i < bytes.length; i++) words[i >> 2] = (words[i >> 2] || 0) | bytes.charCodeAt(i) << (24 - (i % 4) * 8);
    words[bits >> 5] = (words[bits >> 5] || 0) | 0x80 << (24 - bits % 32);
    words[(((bits + 64) >> 9) << 4) + 15] = bits;
    function rotate(x, b) { return (x >>> b) | (x << (32 - b)); }
    for (i = 0; i < words.length; i += 16) {
        var w = [], a = h.slice();
        for (j = 0; j < 64; j++) {
            if (j < 16) w[j] = words[i + j] | 0;
            else {
                var x = w[j - 15], y = w[j - 2];
                w[j] = (w[j - 16] + (rotate(x, 7) ^ rotate(x, 18) ^ (x >>> 3)) + w[j - 7] + (rotate(y, 17) ^ rotate(y, 19) ^ (y >>> 10))) | 0;
            }
            var t1 = (a[7] + (rotate(a[4], 6) ^ rotate(a[4], 11) ^ rotate(a[4], 25)) +
                ((a[4] & a[5]) ^ (~a[4] & a[6])) + k[j] + w[j]) | 0;
            var t2 = ((rotate(a[0], 2) ^ rotate(a[0], 13) ^ rotate(a[0], 22)) +
                ((a[0] & a[1]) ^ (a[0] & a[2]) ^ (a[1] & a[2]))) | 0;
            a = [(t1 + t2) | 0, a[0], a[1], a[2], (a[3] + t1) | 0, a[4], a[5], a[6]];
        }
        for (j = 0; j < 8; j++) h[j] = (h[j] + a[j]) | 0;
    }
    return h.map(function (x) { return ('00000000' + (x >>> 0).toString(16)).slice(-8); }).join('');
}
function exists(path) { return FS.fileExistsAtPath(path); }
function read(path) {
    noLinks(path);
    var value = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
    check(value && !value.isNil(), 'Cannot read ' + path);
    return ObjC.unwrap(value);
}
function json(path) { var value = JSON.parse(read(path)); safeObject(value); return value; }
function noLinks(path) {
    var parts = path.split('/'), prefix = '';
    parts.forEach(function (part) {
        if (!part) return;
        prefix += '/' + part;
        if (exists(prefix)) {
            var attrs = FS.attributesOfItemAtPathError(prefix, null);
            check(ObjC.unwrap(attrs.objectForKey('NSFileType')) !== 'NSFileTypeSymbolicLink', 'Symlinks are not accepted: ' + prefix);
        }
    });
}
function directory(path) { noLinks(path); check(FS.createDirectoryAtPathWithIntermediateDirectoriesAttributesError(path, true, $(), null), 'Cannot create private folder'); }
function write(path, value, replace) {
    noLinks(path);
    check(replace || !exists(path), 'Refusing to overwrite accepted file');
    var pending = path.slice(0, path.lastIndexOf('/')) + '/.pending-' + token();
    check($(value).writeToFileAtomicallyEncodingError(pending, false, $.NSUTF8StringEncoding, null), 'Cannot save private record');
    check(replace || !exists(path), 'Accepted file appeared during save');
    check(nativeRename(pending, path) === 0, 'Cannot atomically commit private record');
}
function writeJSON(path, value, replace) { write(path, JSON.stringify(value, null, 2) + '\n', replace); }
function names(path) { if (!exists(path)) return []; return ObjC.deepUnwrap(FS.contentsOfDirectoryAtPathError(path, null)); }
function token() { return ObjC.unwrap($.NSUUID.UUID.UUIDString); }
function workspacePath(value) {
    var result = value || home + '/Library/Application Support/Support Release Readiness/workspaces/default';
    check(result.charAt(0) === '/' && result.indexOf('/../') < 0 && result.indexOf('/./') < 0 && !/\/$/.test(result), 'Workspace needs a clean absolute path');
    var scripts = ObjC.deepUnwrap($.NSProcessInfo.processInfo.arguments).filter(function (p) { return /\.js$/i.test(p); });
    check(scripts.length > 0, 'Cannot identify the agent download; private work was not opened');
    var script = scripts[0].charAt(0) === '/' ? scripts[0] : ObjC.unwrap(FS.currentDirectoryPath) + '/' + scripts[0];
    script = ObjC.unwrap($(script).stringByResolvingSymlinksInPath);
    check(/\/tools\/records\.js$/i.test(script), 'Cannot identify the agent download; private work was not opened');
    var product = script.slice(0, -'/tools/records.js'.length).toLowerCase();
    var ancestor = result, remainder = '';
    while (!exists(ancestor)) {
        var slash = ancestor.lastIndexOf('/');
        remainder = ancestor.slice(slash) + remainder; ancestor = ancestor.slice(0, slash) || '/';
    }
    var resolvedWork = (ObjC.unwrap($(ancestor).stringByResolvingSymlinksInPath).replace(/\/$/, '') + remainder).toLowerCase();
    check(resolvedWork !== product && resolvedWork.indexOf(product + '/') !== 0, 'Keep private work outside the replaceable agent download');
    noLinks(result); return result;
}
function discoverWorkspaces(base) {
    return names(base).filter(function (name) { return /^[a-z0-9][a-z0-9-]*$/.test(name) && exists(base + '/' + name + '/workspace.json'); }).map(function (name) {
        var path = base + '/' + name;
        try { var data = load(path); return {workspace: path, company: data.state.profile.company || 'Setup incomplete', revision: data.revision, workspace_id: data.meta.id}; }
        catch (error) { return {workspace: path, problem: String(error)}; }
    });
}
function emptyState() { return {profile: {status: 'draft'}, releases: {}}; }
function load(root) {
    check(exists(root + '/workspace.json'), 'Workspace is not set up');
    var meta = json(root + '/workspace.json');
    check(meta.schema === 1 && meta.kind === 'support-release-readiness', 'Unsupported workspace schema; records were not changed');
    var records = names(root + '/records').filter(function (name) { return name.indexOf('.pending-') !== 0; }).sort(), previous = null, state = emptyState(), revision = 0, events = [];
    records.forEach(function (name) {
        check(/^\d{8}\.json$/.test(name), 'Unexpected history file; preserve it and check for a sync conflict');
        var raw = read(root + '/records/' + name), record = JSON.parse(raw); safeObject(record);
        check(record.schema === 1 && record.workspace_id === meta.id, 'History belongs to another workspace or schema');
        check(record.revision === revision + 1 && name === ('00000000' + record.revision).slice(-8) + '.json', 'Missing or conflicting history revision');
        var claimed = record.checksum; delete record.checksum;
        check(sha256(JSON.stringify(record)) === claimed && record.previous_hash === previous, 'History integrity failed at ' + name + '; preserve records and stop');
        check(object(record.state) && object(record.state.profile) && object(record.state.releases), 'Invalid saved state');
        previous = claimed; revision = record.revision; state = record.state; events.push(record.event);
    });
    return {meta: meta, state: state, revision: revision, hash: previous, events: events};
}
function kernelLock(root) {
    noLinks(root + '/writer.lock');
    var fd = nativeOpen(root + '/writer.lock', 514, 384);
    check(fd >= 0, 'Cannot open workspace lock');
    if (nativeFlock(fd, 6) !== 0) { nativeClose(fd); return null; }
    return fd;
}
function lock(root) {
    var fd = kernelLock(root);
    check(fd !== null, 'Another writer holds the native workspace lock');
    var path = root + '/write-lock';
    if (mkdirNative(path, 448) !== 0) { nativeClose(fd); fail('An interrupted save holds lock metadata; inspect status before recovery'); }
    var held = {token: token(), pid: processID, created_at: new Date().toISOString(), fd: fd};
    try { writeJSON(path + '/owner.json', held, false); }
    catch (error) { FS.removeItemAtPathError(path, null); nativeClose(fd); throw error; }
    return held;
}
function unlock(root, held) {
    var path = root + '/write-lock';
    try { if (exists(path + '/owner.json') && json(path + '/owner.json').token === held.token) FS.removeItemAtPathError(path, null); }
    finally { nativeClose(held.fd); }
}
function getRelease(state, releaseID) { id(releaseID); check(own(state.releases, releaseID), 'Unknown release'); return state.releases[releaseID]; }
function currentSource(release, sourceID) {
    id(sourceID); check(own(release.sources, sourceID), 'Unknown source: ' + sourceID);
    var source = release.sources[sourceID]; return source.versions.filter(function (v) { return v.version === source.current; })[0];
}
function normalize(value) { return value.normalize('NFC').replace(/[‘’]/g, "'").replace(/[“”]/g, '"').replace(/\s+/g, ' ').trim(); }
function resolveQuote(body, quote) {
    text(quote, 'Source quote'); check(quote.length <= 12000, 'Select a shorter source passage');
    if (body.indexOf(quote) >= 0) return quote;
    var target = normalize(quote), paragraphs = body.split(/\n\s*\n/), match = null;
    paragraphs.some(function (p) { if (normalize(p).indexOf(target) >= 0) { match = p; return true; } return false; });
    check(match !== null && match.length <= 12000, 'Quote is absent from source; use a current original passage'); return match;
}
function citations(root, release, refs, requireCurrent, requireRecord) {
    check(Array.isArray(refs), 'Evidence must be a list');
    return refs.map(function (ref) {
        id(ref.source_id); text(ref.version, 'Source version');
        check(own(release.sources, ref.source_id), 'Evidence is from an unavailable source/release');
        var source = release.sources[ref.source_id], version = source.versions.filter(function (v) { return v.version === ref.version; })[0];
        check(version, 'Unavailable source version');
        check(!requireCurrent || source.current === version.version, 'Evidence version is no longer current');
        check(!requireRecord || (version.kind === 'record' && version.authority !== 'draft'), 'Completion needs current non-draft records, not an assertion');
        var body = read(root + '/sources/' + version.hash + '.txt');
        check(sha256(body) === version.hash, 'Source integrity failed');
        check(!(own(ref, 'fact') && own(ref, 'quote')), 'Choose a fact selector or a quote, not both');
        var quoted = ref.quote;
        if (own(ref, 'fact')) { check(own(version.facts, ref.fact), 'Unknown source fact selector'); quoted = version.facts[ref.fact].quote; }
        return {source_id: ref.source_id, version: ref.version, quote: resolveQuote(body, quoted)};
    });
}
function owner(state, release, value) {
    text(value, 'Owner');
    var people = (state.profile.people || []).concat(release.people || []);
    check(value === 'not verified' || people.indexOf(value) >= 0, 'Owner is not in the supplied company/release people'); return value;
}
function factsChanged(before, after) {
    var keys = Object.keys(before).concat(Object.keys(after)).filter(function (v, i, a) { return a.indexOf(v) === i; });
    return keys.filter(function (key) { return !own(before, key) || !own(after, key) || before[key].value !== after[key].value; });
}
function putAction(root, state, release, input, now) {
    check(object(input), 'Supply an action'); id(input.id);
    var previous = release.actions[input.id], merged = copy(previous || {});
    Object.keys(input).forEach(function (key) { merged[key] = input[key]; }); input = merged;
    text(input.title, 'Action'); text(input.reason, 'Why this work is needed');
    var statuses = ['open', 'in progress', 'reported complete', 'complete', 'needs review'];
    check(statuses.indexOf(input.status) >= 0, 'Unknown action status');
    check(['critical', 'major', 'routine'].indexOf(input.priority) >= 0, 'Unknown action priority');
    check(['planning', 'training', 'help', 'vendors', 'staffing', 'operations', 'communications', 'known issues', 'follow-up'].indexOf(input.area) >= 0, 'Supply the support area');
    check(typeof input.blocks_release === 'boolean', 'State whether this work blocks the supplied rollout');
    check(Array.isArray(input.depends_on), 'State the action dependencies');
    var minimumAcceptanceRevision = previous ? (previous.reopened_at_revision || 0) : 0;
    input.depends_on.forEach(function (dep) { var source = currentSource(release, dep.source_id); check(own(source.facts, dep.fact), 'Unknown dependency fact'); check(input.status !== 'complete' || source.authority !== 'draft', 'A draft dependency cannot establish completion'); minimumAcceptanceRevision = Math.max(minimumAcceptanceRevision, source.saved_revision); });
    var refs = citations(root, release, input.evidence || [], true, input.status === 'complete');
    var acceptance = [];
    if (input.status === 'complete') {
        check(refs.length > 0, 'Completion needs evidence');
        owner(state, release, input.accepted_by); check(input.accepted_by !== 'not verified', 'Completion needs a named accepting person');
        acceptance = citations(root, release, input.acceptance_evidence || [], true, false);
        check(acceptance.length > 0 && acceptance.some(function (ref) { return currentSource(release, ref.source_id).attribution === input.accepted_by; }), 'Supply the accepting person\'s explicit attributed confirmation');
        check(acceptance.some(function (ref) { var source = currentSource(release, ref.source_id); return source.attribution === input.accepted_by && source.saved_revision >= minimumAcceptanceRevision; }), 'Acceptance predates the changed dependency; obtain current confirmation');
        input.depends_on.forEach(function (dep) {
            var source = currentSource(release, dep.source_id);
            check(refs.some(function (ref) { return ref.source_id === dep.source_id && ref.version === source.version && normalize(ref.quote).indexOf(normalize(source.facts[dep.fact].quote)) >= 0; }), 'Action ' + input.id + ': completion evidence must cover ' + dep.source_id + '.' + dep.fact + ' at ' + source.version);
        });
    }
    release.actions[input.id] = {id: input.id, title: input.title, reason: input.reason, owner: owner(state, release, input.owner),
        status: input.status, priority: input.priority, area: input.area, blocks_release: input.blocks_release, due: input.due || 'not verified',
        depends_on: copy(input.depends_on), evidence: refs, acceptance_evidence: acceptance, accepted_by: input.status === 'complete' ? input.accepted_by : null,
        reopened_at_revision: previous ? (previous.reopened_at_revision || null) : null, updated_at: now};
}
function calculate(input) {
    if (input.kind === 'deadline') {
        var launch = instant(input.launch), rule = input.rule;
        check(object(rule) && ['hours', 'calendar_days', 'business_days'].indexOf(rule.unit) >= 0, 'Choose elapsed hours, calendar days or business days');
        var amount = number(rule.amount, 'Notice lead'); check(amount > 0 && amount <= 3660, 'Notice lead is out of range');
        var date;
        if (rule.unit === 'hours') date = new Date(launch.getTime() - amount * 3600000);
        else {
            check(Math.floor(amount) === amount, 'Day rules need a whole number');
            var zone = $.NSTimeZone.timeZoneWithName(text(rule.timezone, 'Company timezone'));
            check(zone && !zone.isNil(), 'Unknown company timezone');
            var cal = $.NSCalendar.calendarWithIdentifier($.NSCalendarIdentifierGregorian); cal.timeZone = zone;
            var nativeDate = $.NSDate.dateWithTimeIntervalSince1970(launch.getTime() / 1000);
            if (rule.unit === 'calendar_days') nativeDate = cal.dateByAddingUnitValueToDateOptions($.NSCalendarUnitDay, -amount, nativeDate, 0);
            else {
                check(rule.calendar_confirmed === true && Array.isArray(rule.holidays), 'Business-day rule needs a confirmed holiday calendar, even if empty');
                rule.holidays.forEach(function (day) { check(/^\d{4}-\d\d-\d\d$/.test(day), 'Invalid holiday date'); });
                var formatter = $.NSDateFormatter.alloc.init; formatter.timeZone = zone; formatter.dateFormat = 'yyyy-MM-dd';
                var left = amount;
                while (left) {
                    nativeDate = cal.dateByAddingUnitValueToDateOptions($.NSCalendarUnitDay, -1, nativeDate, 0);
                    var weekday = Number(cal.componentFromDate($.NSCalendarUnitWeekday, nativeDate));
                    var day = ObjC.unwrap(formatter.stringFromDate(nativeDate));
                    if (weekday !== 1 && weekday !== 7 && rule.holidays.indexOf(day) < 0) left--;
                }
            }
            date = new Date(Number(nativeDate.timeIntervalSince1970) * 1000);
        }
        return {kind: 'deadline', launch_utc: launch.toISOString(), rule: copy(rule), deadline_utc: date.toISOString()};
    }
    if (input.kind === 'capacity') {
        var minutes = number(input.contacts, 'Contacts') * number(input.aht_minutes, 'Handling minutes per contact');
        var hours = minutes / 60, reserve = number(input.reserve_hours, 'Reserve hours');
        check(isFinite(minutes) && isFinite(hours), 'Handling load is too large');
        return {kind: 'capacity', handling_minutes: minutes, required_agent_hours: hours, additional_agent_hours: Math.max(0, hours - reserve), limit: 'Handling load, not a demand or waiting-time forecast'};
    }
    check(input.kind === 'signals' && Array.isArray(input.windows) && input.windows.length === 2, 'Supply two comparable signal windows');
    var durations = [], rates = input.windows.map(function (w) {
        var start = instant(w.start), end = instant(w.end), exposure = number(w.exposure, 'Exposed accounts'), total = number(w.contacts, 'Contacts');
        check(exposure > 0 && end > start && Math.floor(exposure) === exposure && Math.floor(total) === total, 'Positive exposure, integer counts and a valid window are required');
        check(object(w.categories) && Object.keys(w.categories).length > 0, 'Contact categories are required');
        var sum = Object.keys(w.categories).reduce(function (s, key) { var count = number(w.categories[key], 'Category count'); check(Math.floor(count) === count, 'Contact counts must be whole numbers'); return s + count; }, 0);
        check(sum === total, 'Categories must sum to the contact total'); durations.push(end - start); return total / exposure * 1000;
    });
    check(durations[0] === durations[1], 'Unequal reporting windows cannot be compared');
    return {kind: 'signals', windows: copy(input.windows), baseline_per_1000: rates[0], rollout_per_1000: rates[1],
        rate_ratio: rates[0] === 0 ? null : rates[1] / rates[0], rate_increase_per_1000: rates[1] - rates[0],
        contact_count_increase: input.windows[1].contacts - input.windows[0].contacts,
        limit: 'Rates describe supplied windows; counts are not proof of cause or refund entitlement'};
}
function md(value) { return String(value === null || value === undefined ? '' : value).replace(/\|/g, '\\|').replace(/[\r\n]+/g, ' '); }
function csv(value) {
    var str = String(value === null || value === undefined ? '' : value);
    if (/^[\s]*[=+\-@]/.test(str)) str = "'" + str;
    return '"' + str.replace(/"/g, '""') + '"';
}
function views(data) {
    var tracker = '# Support release work\n\nSaved revision ' + data.revision + '. Reported completion is not verified completion.\n';
    var history = '# Decision and work history\n\n';
    data.events.forEach(function (event, i) { history += (i + 1) + '. ' + md(event.at) + ' — ' + md(event.actor) + ': ' + md(event.summary) + '\n'; });
    Object.keys(data.state.releases).sort().forEach(function (key) {
        var r = data.state.releases[key];
        tracker += '\n## ' + md(r.name) + ' (' + key + ')\n\n' + md(r.phase) + '. Launch: ' + md(r.launch || 'not verified') + '\n\n';
        tracker += '| ID | Work | Owner | Due | Status | Priority |\n| --- | --- | --- | --- | --- | --- |\n';
        Object.keys(r.actions).sort().forEach(function (key) { var a = r.actions[key]; tracker += '| ' + [a.id, a.title, a.owner, a.due, a.status, a.priority].map(md).join(' | ') + ' |\n'; });
    });
    return {'tracker.md': tracker, 'history.md': history};
}
function viewManifest(root) {
    try { var value = json(root + '/views/manifest.json'); return object(value.hashes) && typeof value.revision === 'number' ? value : null; }
    catch (error) { return null; }
}
function viewsNeedRebuild(root, data) {
    var manifest = viewManifest(root);
    return !manifest || ['tracker.md', 'history.md'].some(function (name) { return !exists(root + '/views/' + name); }) || manifest.revision !== data.revision;
}
function changedViews(root, data) {
    var manifest = viewManifest(root), expected = views(data || load(root));
    return ['tracker.md', 'history.md'].filter(function (name) {
        if (!exists(root + '/views/' + name)) return false;
        var actual = sha256(read(root + '/views/' + name));
        return actual !== sha256(expected[name]) && (!manifest || actual !== manifest.hashes[name]);
    });
}
function rebuild(root, data, preserve) {
    var edited = changedViews(root, data), kept = [];
    check(!edited.length || preserve === true, 'Manual tracker/history edits found; preserve them as reply material before rebuilding');
    edited.forEach(function (name) {
        var dest = root + '/inbox/view-edits-' + data.revision + '-' + token() + '-' + name;
        write(dest, read(root + '/views/' + name), false); kept.push(dest);
    });
    directory(root + '/views'); var rendered = views(data), hashes = {};
    Object.keys(rendered).forEach(function (name) { write(root + '/views/' + name, rendered[name], true); hashes[name] = sha256(rendered[name]); });
    writeJSON(root + '/views/manifest.json', {revision: data.revision, hashes: hashes}, true); return kept;
}
function summary(root, data) {
    var releases = Object.keys(data.state.releases).map(function (key) {
        var r = data.state.releases[key];
        var latest = r.reviews.length ? r.reviews[r.reviews.length - 1] : null;
        return {id: key, name: r.name, phase: r.phase, launch: r.launch || null, action_counts: Object.keys(r.actions).reduce(function (counts, id) {
            var status = r.actions[id].status; counts[status] = (counts[status] || 0) + 1; return counts;
        }, {}), latest_review: latest ? latest.recommendation : 'not reviewed', review_is_current: Boolean(latest && latest.saved_revision === r.updated_revision && latest.profile_revision === data.state.profile_revision)};
    });
    var held = null;
    if (exists(root + '/write-lock')) {
        try { held = json(root + '/write-lock/owner.json'); held.owner_alive = processAlive(held.pid); }
        catch (error) { held = {token: 'incomplete-owner-record', pid: null, owner_alive: null, problem: 'Interrupted before lock metadata was saved'}; }
    }
    return {workspace: root, workspace_id: data.meta.id, revision: data.revision, profile: data.state.profile, releases: releases,
        manual_view_edits: changedViews(root, data), lock: held, inbox: names(root + '/inbox'),
        views_need_rebuild: viewsNeedRebuild(root, data)};
}
function mutate(root, data, operation, request, now) {
    var state = data.state, r, result = {};
    if (operation === 'intake') {
        check(Array.isArray(request.sources) && request.sources.length > 0, 'Supply sources to import together');
        return {imported: request.sources.map(function (source) {
            var part = {release_id: request.release_id, source: source};
            return {id: source.id, version: source.version, result: mutate(root, data, 'source', part, now)};
        })};
    }
    if (operation === 'profile') {
        check(object(request.profile), 'Supply company context');
        var profile = copy(request.profile);
        check(['draft', 'confirmed'].indexOf(profile.status) >= 0, 'Profile must be draft or confirmed');
        if (profile.status === 'confirmed') {
            text(profile.company, 'Company'); text(profile.support_model, 'Support model'); text(profile.timezone, 'Timezone');
            check(Array.isArray(profile.people) && profile.people.length > 0, 'Supply named people');
            profile.people.forEach(function (p) { text(p, 'Person'); });
            check(object(profile.notice_rule), 'Clarify the notice rule');
            calculate({kind: 'deadline', launch: '2026-10-20T10:00:00Z', rule: profile.notice_rule});
            text(profile.launch_authority, 'Launch authority or not verified');
        }
        state.profile = profile; state.profile_revision = data.revision + 1;
    } else if (operation === 'release') {
        id(request.release_id); text(request.name, 'Release name');
        check(['planning', 'prelaunch', 'rollout', 'follow-up'].indexOf(request.phase) >= 0, 'Unknown release phase');
        if (request.launch) instant(request.launch);
        if (!own(state.releases, request.release_id)) state.releases[request.release_id] = {id: request.release_id, sources: {}, actions: {}, reviews: [], decisions: [], people: []};
        r = getRelease(state, request.release_id); r.name = request.name; r.phase = request.phase;
        r.launch = request.launch || null; r.scope = text(request.scope, 'Release scope');
        r.people = request.people || r.people;
        check(Array.isArray(r.people), 'People must be a list'); r.people.forEach(function (p) { text(p, 'Person'); });
    } else {
        r = getRelease(state, request.release_id);
        if (operation === 'source') {
            var s = request.source; check(object(s), 'Supply a source'); id(s.id); text(s.version, 'Source version'); text(s.title, 'Source title');
            text(s.attribution, 'Source attribution'); instant(s.observed_at);
            var origin = {kind: 'supplied text or attributed extract'};
            if (own(s, 'file')) {
                check(!own(s, 'content'), 'Choose an original text file or supplied text, not both');
                var prefix = root + '/inbox/'; text(s.file, 'Source file');
                check(s.file.indexOf(prefix) === 0 && s.file.slice(prefix.length).split('/').every(function (p) { return p && p !== '.' && p !== '..'; }), 'Source file must be inside the selected workspace inbox');
                check(/\.(md|txt|csv|json)$/i.test(s.file), 'Source file needs a readable text extract');
                noLinks(s.file);
                var sourceBytes = Number(ObjC.unwrap(FS.attributesOfItemAtPathError(s.file, null).objectForKey('NSFileSize')));
                check(isFinite(sourceBytes) && sourceBytes <= 2000000, 'Source is too large; choose a relevant text extract');
                s.content = read(s.file); origin = {kind: 'workspace text file', path: s.file.slice((root + '/').length)};
            }
            text(s.content, 'Source content');
            check(s.content.length <= 2000000, 'Source is too large; choose a relevant extract');
            check(['draft', 'approved', 'observed'].indexOf(s.authority) >= 0 && ['record', 'attestation'].indexOf(s.kind) >= 0, 'State source authority and record/attestation kind');
            var source = r.sources[s.id] || {current: null, versions: []};
            check(!source.versions.some(function (v) { return v.version === s.version; }), 'Source version already exists; preserve it and supply a new version');
            var facts = s.facts || {}; check(object(facts), 'Facts must be keyed records');
            Object.keys(facts).forEach(function (key) { text(key, 'Fact key'); text(facts[key].value, 'Fact value'); facts[key].quote = resolveQuote(s.content, facts[key].quote); });
            var previous = source.current ? currentSource(r, s.id) : null;
            var stored = {version: s.version, title: s.title, attribution: s.attribution, authority: s.authority, kind: s.kind,
                observed_at: s.observed_at, hash: sha256(s.content), facts: facts, saved_revision: data.revision + 1, origin: origin};
            var blob = root + '/sources/' + stored.hash + '.txt';
            if (exists(blob)) check(read(blob) === s.content, 'Source blob conflict'); else write(blob, s.content, false);
            source.versions.push(stored); r.sources[s.id] = source;
            if (!previous || s.authority !== 'draft' || previous.authority === 'draft') {
                source.current = s.version;
                var changed = previous ? factsChanged(previous.facts, facts) : [];
                Object.keys(r.actions).forEach(function (key) {
                    var a = r.actions[key];
                    if (a.depends_on.some(function (dep) { return dep.source_id === s.id && changed.indexOf(dep.fact) >= 0; })) {
                        a.status = 'needs review'; a.updated_at = now; a.reopened_because = 'Changed ' + s.id + ': ' + changed.join(', ');
                        a.reopened_at_revision = data.revision + 1;
                    }
                });
                result.changed_facts = changed;
            } else result.pending_draft = true;
        } else if (operation === 'action') putAction(root, state, r, request.action, now);
        else if (operation === 'review') {
            var review = request.review;
            check(object(review), 'Supply a review');
            check(['continue discovery', 'support not ready', 'support ready for the specified rollout', 'recommend pause', 'continue monitoring', 'follow-up incomplete', 'follow-up complete', 'not verified'].indexOf(review.recommendation) >= 0, 'Unknown readiness recommendation');
            text(review.summary, 'Review summary'); check(Array.isArray(review.findings) && Array.isArray(review.unknowns), 'Supply findings and unknowns');
            (review.actions || []).forEach(function (a) { putAction(root, state, r, a, now); });
            var refs = citations(root, r, review.evidence || [], true, false); check(refs.length > 0, 'Review needs current evidence');
            review.findings.forEach(function (f) { text(f.statement, 'Finding'); check(['critical', 'major', 'routine'].indexOf(f.priority) >= 0, 'Finding priority required'); f.evidence = citations(root, r, f.evidence || [], true, false); check(f.evidence.length > 0, 'Finding needs current evidence'); });
            review.observations = review.observations || [];
            check(Array.isArray(review.observations), 'Observations must be a list');
            review.observations.forEach(function (o) { text(o.statement, 'Observation'); o.evidence = citations(root, r, o.evidence || [], true, false); check(o.evidence.length > 0, 'Observation needs current evidence'); });
            if (review.recommendation === 'support ready for the specified rollout') {
                check(r.phase === 'prelaunch', 'Ready recommendation belongs to a specified prelaunch rollout');
                check(!review.findings.some(function (f) { return f.priority === 'critical' || f.priority === 'major'; }), 'Open serious findings prevent ready; put resolved work and separate authority states in observations');
                check(!Object.keys(r.actions).some(function (key) { var a = r.actions[key]; return a.status === 'needs review' || (a.blocks_release && a.status !== 'complete'); }), 'Unresolved or changed blocking work prevents a ready recommendation');
                var required = ['planning', 'training', 'help', 'vendors', 'staffing', 'operations', 'communications', 'known issues'];
                check(Array.isArray(review.coverage), 'Ready recommendation needs preparation coverage');
                required.forEach(function (area) {
                    var covered = review.coverage.filter(function (c) { return c.area === area; });
                    check(covered.length === 1 && ['verified', 'not applicable'].indexOf(covered[0].status) >= 0, 'Preparation not established for ' + area);
                    text(covered[0].reason, 'Coverage reason');
                    covered[0].evidence = citations(root, r, covered[0].evidence || [], true, true);
                    check(covered[0].evidence.length > 0, 'Coverage needs current records');
                });
            }
            if (review.recommendation === 'follow-up complete') check(r.phase === 'follow-up' && !Object.keys(r.actions).some(function (key) { var a = r.actions[key]; return a.area === 'follow-up' && a.status !== 'complete'; }), 'Unresolved customer follow-up prevents completion');
            review.evidence = refs; review.at = now; review.as_of = review.as_of ? instant(review.as_of).toISOString() : now;
            review.saved_revision = data.revision + 1;
            review.profile_revision = state.profile_revision;
            review.calculations = (review.calculation_requests || []).map(calculate); delete review.calculation_requests; delete review.actions;
            r.reviews.push(copy(review)); result.recommendation = review.recommendation;
        } else if (operation === 'decision') {
            var decision = request.decision; check(object(decision), 'Supply a reported human decision');
            check(['launch', 'pause', 'resume', 'follow-up', 'other'].indexOf(decision.kind) >= 0, 'Unknown decision kind');
            owner(state, r, decision.person); check(decision.person !== 'not verified', 'Name the human decision maker'); text(decision.statement, 'Reported decision');
            var proof = citations(root, r, decision.evidence || [], true, false); check(proof.length > 0, 'Reported decision needs attribution and evidence');
            r.decisions.push({kind: decision.kind, person: decision.person, statement: decision.statement, evidence: proof, at: now, status: 'reported human decision; no action executed by agent'});
        } else fail('Unknown mutation');
    }
    if (r) r.updated_revision = data.revision + 1;
    return result;
}
function shared(root, data, request) {
    var r = getRelease(data.state, request.release_id), actions = Object.keys(r.actions).map(function (key) { return r.actions[key]; });
    var latest = r.reviews.length ? r.reviews[r.reviews.length - 1] : null;
    var current = Boolean(latest && latest.saved_revision === r.updated_revision && latest.profile_revision === data.state.profile_revision);
    var brief = '# ' + md(r.name) + ' — support readiness\n\nGenerated ' + new Date().toISOString() + '; saved revision ' + data.revision + '.\n\n';
    brief += 'Review as of: ' + md(latest ? (latest.as_of || 'not recorded') : 'not reviewed') + '.\n\n';
    brief += 'Scope: ' + md(r.scope) + '\n\nPhase: ' + md(r.phase) + '. Launch: ' + md(r.launch || 'not verified') + '.\n\n';
    brief += 'Latest saved recommendation: ' + md(latest ? latest.recommendation : 'not reviewed') + '. ' + (current ? 'Current for these saved records.' : 'Requires a new review; relevant records changed or no review is saved.') + '\n\n';
    brief += 'Reported completion is not verified completion. Human launch/pause/resumption authority remains separate. This agent has sent no messages and taken no launch/customer action.\n\n';
    brief += '| ID | Work | Owner | Due | Status | Priority |\n| --- | --- | --- | --- | --- | --- |\n';
    var rows = [['Release', 'Action ID', 'Work', 'Owner', 'Due', 'Status', 'Priority']];
    actions.forEach(function (a) { brief += '| ' + [a.id, a.title, a.owner, a.due, a.status, a.priority].map(md).join(' | ') + ' |\n'; rows.push([r.id, a.id, a.title, a.owner, a.due, a.status, a.priority]); });
    brief += '\n## Decisions reported by people\n\n';
    r.decisions.forEach(function (d) { brief += '- ' + md(d.person) + ': ' + md(d.statement) + ' (' + md(d.status) + ')\n'; });
    brief += '\n## Reply with updates\n\nUse the action ID, what changed, who confirmed it and any supporting record. Give this reply to the support lead to bring back into the agent. Review the brief for sensitive names or work descriptions before sharing. Source documents and quotations are excluded.\n';
    var dest = root + '/shared/' + r.id + '-r' + data.revision + '-' + token(); directory(dest);
    write(dest + '/brief.md', brief, false); write(dest + '/actions.csv', rows.map(function (row) { return row.map(csv).join(','); }).join('\r\n') + '\r\n', false);
    return {brief: dest + '/brief.md', actions: dest + '/actions.csv', revision: data.revision, review_privacy_before_sharing: true};
}
function run(argv) {
    ObjC.import('Foundation'); ObjC.bindFunction('mkdir', ['int', ['char *', 'int']]); ObjC.bindFunction('kill', ['int', ['int', 'int']]);
    ObjC.bindFunction('creat', ['int', ['char *', 'int']]); ObjC.bindFunction('flock', ['int', ['int', 'int']]);
    ObjC.bindFunction('close', ['int', ['int']]); ObjC.bindFunction('rename', ['int', ['char *', 'char *']]);
    nativeOpen = function (p, f, m) { return $.creat(p, m); }; nativeFlock = function (fd, f) { return $.flock(fd, f); };
    nativeClose = function (fd) { return $.close(fd); }; nativeRename = function (a, b) { return $.rename(a, b); };
    FS = $.NSFileManager.defaultManager; home = ObjC.unwrap($.NSHomeDirectory()); mkdirNative = function (p, mode) { return $.mkdir(p, mode); };
    processID = Number($.NSProcessInfo.processInfo.processIdentifier);
    processAlive = function (pid) { check(typeof pid === 'number' && Math.floor(pid) === pid && pid > 0, 'Invalid lock owner PID'); return $.kill(pid, 0) === 0; };
    var operation = argv[0], root = workspacePath(argv[1]);
    if (operation === 'home') {
        var base = home + '/Library/Application Support/Support Release Readiness/workspaces';
        return JSON.stringify({workspace: root, workspaces_root: base, existing_workspaces: argv[1] ? (exists(root + '/workspace.json') ? [{workspace: root, company: load(root).state.profile.company || 'Setup incomplete'}] : []) : discoverWorkspaces(base), interpreter: 'macOS system JavaScript', installs_needed: false});
    }
    if (operation === 'setup') {
        directory(root); var existing = names(root);
        check(exists(root + '/workspace.json') || existing.every(function (name) { return ['requests', 'inbox'].indexOf(name) >= 0; }), 'Choose an empty private folder, not an existing document/project folder');
        var setupLock = lock(root);
        try {
            ['records', 'sources', 'requests', 'inbox', 'shared', 'views'].forEach(function (name) { directory(root + '/' + name); });
            if (!exists(root + '/workspace.json')) writeJSON(root + '/workspace.json', {schema: 1, kind: 'support-release-readiness', id: token()}, false);
            var initial = load(root); rebuild(root, initial, false); return JSON.stringify(summary(root, initial));
        } finally { unlock(root, setupLock); }
    }
    var data = load(root);
    if (operation === 'status') return JSON.stringify(summary(root, data));
    var requestPath = text(argv[2], 'Request file');
    check(requestPath.indexOf(root + '/requests/') === 0 && /^[a-zA-Z0-9_-]+\.json$/.test(requestPath.slice((root + '/requests/').length)), 'Request must be a JSON file directly inside this workspace requests folder');
    check(read(requestPath).length <= 3000000, 'Request too large'); var request = json(requestPath);
    if (operation === 'calculate') return JSON.stringify(calculate(request));
    if (operation === 'inspect') {
        var r = getRelease(data.state, request.release_id), selected = copy(r); selected.sources = {};
        selected.reviews_total = r.reviews.length;
        if (request.include_history !== true) selected.reviews = r.reviews.slice(-1);
        (request.source_ids || Object.keys(r.sources)).forEach(function (sourceID) {
            var version = copy(currentSource(r, sourceID)), body = read(root + '/sources/' + version.hash + '.txt');
            check(sha256(body) === version.hash, 'Source integrity failed'); version.content = body; selected.sources[sourceID] = version;
        });
        return JSON.stringify({revision: data.revision, profile: data.state.profile, release: selected});
    }
    check(request.expected_revision === data.revision, 'Stale revision; reload current work before saving');
    if (operation === 'recover-lock') {
        var recoveryFD = kernelLock(root); check(recoveryFD !== null, 'Cannot recover an active writer lock');
        try {
            var oldLock;
            try { oldLock = json(root + '/write-lock/owner.json'); }
            catch (error) { oldLock = {token: 'incomplete-owner-record', pid: null}; }
            check(exists(root + '/write-lock') && request.confirm_recovery === true && request.lock_token === oldLock.token &&
                (oldLock.pid === null || !processAlive(oldLock.pid)), 'Lock recovery requires explicit confirmation, matching token and a dead owner');
            writeJSON(root + '/inbox/recovered-lock-' + token() + '.json', oldLock, false);
            FS.removeItemAtPathError(root + '/write-lock', null); return JSON.stringify({recovered: true, revision: data.revision});
        } finally { nativeClose(recoveryFD); }
    }
    var held = lock(root);
    try {
        data = load(root); check(request.expected_revision === data.revision, 'Stale revision; another writer saved first');
        if (operation === 'rebuild') return JSON.stringify({revision: data.revision, preserved_edits: rebuild(root, data, request.preserve_edits)});
        check(changedViews(root, data).length === 0, 'Manual view edits found; preserve them before changing or rebuilding work');
        if (viewsNeedRebuild(root, data)) rebuild(root, data, false);
        if (operation === 'export') return JSON.stringify(shared(root, data, request));
        check(['profile', 'release', 'source', 'intake', 'action', 'review', 'decision'].indexOf(operation) >= 0, 'Unknown operation');
        var now = new Date().toISOString(); text(request.actor, 'Who supplied this update'); text(request.summary, 'Change summary');
        var result = mutate(root, data, operation, request, now);
        var record = {schema: 1, workspace_id: data.meta.id, revision: data.revision + 1, previous_hash: data.hash,
            event: {at: now, actor: request.actor, operation: operation, release_id: request.release_id || null, summary: request.summary}, state: data.state};
        record.checksum = sha256(JSON.stringify(record));
        var filename = root + '/records/' + ('00000000' + record.revision).slice(-8) + '.json';
        writeJSON(filename, record, false);
        result.revision = record.revision; result.saved = true; result.external_actions_executed = false;
        try { var committed = load(root); rebuild(root, committed, false); }
        catch (error) { result.views_need_rebuild = true; result.warning = 'Records saved; derived views need rebuilding: ' + String(error); }
        return JSON.stringify(result);
    } finally { unlock(root, held); }
}
