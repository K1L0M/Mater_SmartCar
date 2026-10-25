[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Sync', 'Push', 'AfterMerge', 'Publish')]
    [string]$Action,
    [string]$ReleaseMessage = 'Merge develop into main: release'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$exitCode = 0
$returnBranch = $null
$started = $false

function Invoke-Git {
    param([string[]]$GitArgs)
    & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed (exit $LASTEXITCODE). Stop and inspect git status."
    }
}

function Test-Ref {
    param([string]$Ref)
    & git show-ref --verify --quiet $Ref
    if ($LASTEXITCODE -eq 0) { return $true }
    if ($LASTEXITCODE -eq 1) { return $false }
    throw "Cannot inspect ref $Ref."
}

function Test-Ancestor {
    param([string]$Older, [string]$Newer)
    & git merge-base --is-ancestor $Older $Newer
    if ($LASTEXITCODE -eq 0) { return $true }
    if ($LASTEXITCODE -eq 1) { return $false }
    throw "Cannot compare $Older and $Newer."
}

function Get-Tip {
    param([string]$Ref)
    return (Invoke-Git @('rev-parse', '--verify', $Ref)).Trim()
}

function Assert-Clean {
    if (@(Invoke-Git @('status', '--porcelain', '--untracked-files=all')).Count -ne 0) {
        throw 'Working tree is not clean. Commit intended files or stash explicitly, then retry.'
    }
    foreach ($state in @('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply', 'sequencer', 'BISECT_START')) {
        $path = Invoke-Git @('rev-parse', '--git-path', $state)
        if (Test-Path -LiteralPath $path) {
            throw "Unfinished Git operation ($state). Finish or abort it before running this script."
        }
    }
}

function Assert-RemoteTip {
    param([string]$Remote, [string]$Branch, [string]$Expected)
    $line = @(Invoke-Git @('ls-remote', '--exit-code', '--heads', $Remote, "refs/heads/$Branch"))
    if ($line.Count -ne 1 -or ($line[0] -split '\s+')[0] -ne $Expected) {
        throw "$Remote/$Branch changed or did not reach the expected commit. Fetch and retry; no force push was used."
    }
}

Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    $returnBranch = (Invoke-Git @('branch', '--show-current')).Trim()
    if ($returnBranch -notlike 'feature/*') {
        throw 'Start on your own feature/<name> branch. No branches have been switched.'
    }
    Assert-Clean
    $started = $true
    Invoke-Git @('fetch', '--prune', 'origin') | Out-Host
    $developTip = Get-Tip 'refs/remotes/origin/develop'
    $personalRemote = "refs/remotes/origin/$returnBranch"

    # Never discard local develop commits, even when pull --ff-only would say up to date.
    if ((Test-Ref 'refs/heads/develop') -and -not (Test-Ancestor 'refs/heads/develop' $developTip)) {
        throw 'Local develop has commits absent from origin/develop. Back them up and reconcile manually; no reset was performed.'
    }
    if ($Action -eq 'AfterMerge') {
        if (-not (Test-Ancestor 'HEAD' $developTip)) {
            throw 'Personal commits are not all in origin/develop. Merge the PR normally first; squash/rebase merges need manual reconciliation.'
        }
        if ((Test-Ref $personalRemote) -and -not (Test-Ancestor $personalRemote $developTip)) {
            throw 'Remote personal commits are not all in origin/develop. Integrate them before AfterMerge.'
        }
    }
    if ($Action -eq 'Publish') {
        Invoke-Git @('remote', 'get-url', 'github') | Out-Host
        Invoke-Git @('fetch', 'github', 'refs/heads/main') | Out-Host
        $githubMainTip = Get-Tip 'FETCH_HEAD'
        # Allow retrying a locally created release merge, but never silently publish
        # unrelated work committed directly on main.
        if (Test-Ref 'refs/heads/main') {
            foreach ($commit in @(Invoke-Git @('rev-list', '--first-parent', 'origin/main..main'))) {
                $parents = ((Invoke-Git @('rev-list', '--parents', '-n', '1', $commit)).Trim() -split '\s+')
                if ($parents.Count -ne 3 -or -not (Test-Ancestor $parents[2] $developTip)) {
                    throw 'Local main contains unpublished work other than a develop release merge. Review it before publishing.'
                }
            }
        }
    }

    # Checked ancestry above: this only creates or fast-forwards develop.
    # Git also refuses if develop is checked out in another worktree.
    if (-not (Test-Ref 'refs/heads/develop') -or (Get-Tip 'develop') -ne $developTip) {
        Invoke-Git @('branch', '-f', 'develop', $developTip) | Out-Host
    }
    Invoke-Git @('branch', '--set-upstream-to=origin/develop', 'develop') | Out-Host

    switch ($Action) {
        { $_ -in @('Sync', 'Push') } {
            if (Test-Ref $personalRemote) {
                Invoke-Git @('merge', '--no-edit', '--no-autostash', $personalRemote) | Out-Host
            }
            Invoke-Git @('merge', '--no-edit', '--no-autostash', $developTip) | Out-Host
            if ($Action -eq 'Push') {
                Invoke-Git @('push', '-u', 'origin', "HEAD:refs/heads/$returnBranch") | Out-Host
                Assert-RemoteTip 'origin' $returnBranch (Get-Tip 'HEAD')
            }
        }
        'AfterMerge' {
            Invoke-Git @('merge', '--ff-only', '--no-autostash', $developTip) | Out-Host
            Invoke-Git @('push', '-u', 'origin', "HEAD:refs/heads/$returnBranch") | Out-Host
            Assert-RemoteTip 'origin' $returnBranch $developTip
            Assert-RemoteTip 'origin' 'develop' $developTip
            if ((Get-Tip 'HEAD') -ne $developTip -or (Get-Tip 'develop') -ne $developTip) {
                throw 'Post-merge equality check failed.'
            }
            Write-Host "Aligned: local personal, remote personal, local develop, origin/develop = $developTip"
        }
        'Publish' {
            if (Test-Ref 'refs/heads/main') {
                Invoke-Git @('switch', 'main') | Out-Host
            } else {
                Invoke-Git @('switch', '--track', '-c', 'main', 'origin/main') | Out-Host
            }
            Invoke-Git @('merge', '--ff-only', '--no-autostash', 'origin/main') | Out-Host
            Invoke-Git @('merge', '--no-ff', '--no-edit', '--no-autostash', $developTip, '-m', $ReleaseMessage) | Out-Host
            $mainTip = Get-Tip 'HEAD'
            if (-not (Test-Ancestor $githubMainTip $mainTip)) {
                throw 'GitHub main has independent commits. Reconcile them before publishing; no force push was used.'
            }
            Invoke-Git @('push', 'origin', 'refs/heads/main:refs/heads/main') | Out-Host
            Invoke-Git @('push', 'github', 'refs/heads/main:refs/heads/main') | Out-Host
            Assert-RemoteTip 'origin' 'main' $mainTip
            Assert-RemoteTip 'github' 'main' $mainTip
            Write-Host "Verified both main remotes: $mainTip"
        }
    }
    Assert-Clean
    if ($Action -in @('Sync', 'Push')) {
        if ((Get-Tip 'HEAD') -eq $developTip) {
            Write-Host 'Personal branch equals the fetched origin/develop commit.'
        } else {
            Write-Host 'Personal branch contains develop plus personal commits. Merge the PR, then run AfterMerge to obtain identical commits.'
        }
    }
} catch {
    $exitCode = 1
    Write-Error -Message $_.Exception.Message -ErrorAction Continue
    if ($started) {
        try {
            $mergePath = Invoke-Git @('rev-parse', '--git-path', 'MERGE_HEAD')
            if (Test-Path -LiteralPath $mergePath) {
                Invoke-Git @('merge', '--abort') | Out-Host
                Write-Host 'Aborted the merge started by this script. Resolve the conflict manually on your feature branch.'
            }
        } catch {
            Write-Error -Message "Merge cleanup failed: $($_.Exception.Message)" -ErrorAction Continue
        }
    }
} finally {
    if ($started) {
        try {
            $current = (Invoke-Git @('branch', '--show-current')).Trim()
            if ($current -ne $returnBranch) {
                Invoke-Git @('switch', $returnBranch) | Out-Host
            }
            Write-Host "Current branch: $returnBranch"
            Invoke-Git @('status', '--short', '--branch') | Out-Host
        } catch {
            $exitCode = 1
            Write-Error -Message "Could not restore the personal branch: $($_.Exception.Message). Run git status before continuing." -ErrorAction Continue
        }
    }
    Pop-Location
}
exit $exitCode
