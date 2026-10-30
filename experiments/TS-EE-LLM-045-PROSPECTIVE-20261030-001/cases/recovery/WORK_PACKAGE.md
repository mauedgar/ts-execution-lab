Case A: implement recoverAttempt(journal,request) in src/recover.mjs.
journal: array of plain objects, each with nonempty string attemptId,subjectSha,owner, nonnegative safe integer seq, effect exactly NONE/CONFIRMED/UNKNOWN, receipt null or nonempty string. request is three nonempty strings attemptId,subjectSha,owner. Validate all rows including irrelevant rows; reject malformed using TypeError or RangeError; never mutate inputs.
For matching attemptId, if any mismatched subjectSha/owner return {decision:'BLOCK_IDENTITY',effect:'UNKNOWN',receipt:null}.
If no matches return {decision:'ELIGIBLE',effect:'NONE',receipt:null}.
If any matching UNKNOWN return {decision:'RECONCILE',effect:'UNKNOWN',receipt:null} regardless of sequence.
Otherwise if any CONFIRMED: choose matching CONFIRMED highest seq, tie earliest input. If that row receipt null return {decision:'PENDING_RECEIPT',effect:'CONFIRMED',receipt:null}, else {decision:'NO_RETRY',effect:'CONFIRMED',receipt:chosen receipt}.
Otherwise return {decision:'ELIGIBLE',effect:'NONE',receipt:null}. Pure function only. UNKNOWN sticky; missing receipt never authorizes retry. Only src/recover.mjs writable.
