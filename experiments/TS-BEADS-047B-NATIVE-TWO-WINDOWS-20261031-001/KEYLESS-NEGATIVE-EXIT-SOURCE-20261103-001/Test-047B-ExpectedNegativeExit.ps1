# Strictly synthetic native-process exit handling regression.
# This script never invokes Cosign, requests OIDC, or signs any bytes.
[CmdletBinding()]
param(
  [ValidateRange(0,255)]
  [int]$ExpectedRejectedExitCode=17
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT){
  throw 'WINDOWS_REQUIRED'
}
$native=[Environment]::GetEnvironmentVariable('ComSpec')
if([string]::IsNullOrWhiteSpace($native) -or
    -not [IO.File]::Exists($native)){
  throw 'NATIVE_TEST_BINARY_MISSING'
}
# Deterministic, local, no IO: a rejected mock verification returns 17.
& $native /D /C 'exit /b 17'
$rejectedExit=$LASTEXITCODE
if($rejectedExit -eq 0){
  throw 'NEGATIVE_MOCK_UNEXPECTED_SUCCESS'
}
if($rejectedExit -ne $ExpectedRejectedExitCode){
  throw 'NEGATIVE_MOCK_EXIT_MISMATCH'
}
'EXPECTED_NEGATIVE_PROCESS_REJECTED'
# Explicitly resolve the previously nonzero native exit when the negative
# condition was expected. GitHub's pwsh wrapper must not inherit 17.
exit 0
