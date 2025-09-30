# PowerShell Script to Push to GitHub
# Run this script from the Exam-System directory

Write-Host "🚀 GitHub Push Script" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/" -ForegroundColor Yellow
    exit
}

Write-Host "✅ Git is installed" -ForegroundColor Green
Write-Host ""

# Check if already a git repository
if (!(Test-Path ".git")) {
    Write-Host "📁 Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "📝 Adding files to Git..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "💬 Creating commit..." -ForegroundColor Yellow
$commitMessage = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Initial commit: Complete Exam Proctoring System"
}
git commit -m "$commitMessage"

Write-Host ""
Write-Host "🌐 Now you need to create a repository on GitHub:" -ForegroundColor Cyan
Write-Host "1. Go to https://github.com/new" -ForegroundColor White
Write-Host "2. Repository name: DS_Exam_Proctaring" -ForegroundColor White
Write-Host "3. Description: Distributed Exam Proctoring System" -ForegroundColor White
Write-Host "4. Choose Public or Private" -ForegroundColor White
Write-Host "5. DO NOT initialize with README" -ForegroundColor White
Write-Host "6. Click 'Create repository'" -ForegroundColor White
Write-Host ""

$continue = Read-Host "Have you created the repository on GitHub? (y/n)"
if ($continue -ne "y") {
    Write-Host "⏸️  Paused. Run this script again after creating the repository." -ForegroundColor Yellow
    exit
}

Write-Host ""
$username = Read-Host "Enter your GitHub username"
$repoName = Read-Host "Enter repository name (default: DS_Exam_Proctaring)"
if ([string]::IsNullOrWhiteSpace($repoName)) {
    $repoName = "DS_Exam_Proctaring"
}

Write-Host ""
Write-Host "🔗 Adding remote repository..." -ForegroundColor Yellow
git remote add origin "https://github.com/$username/$repoName.git"
git branch -M main

Write-Host ""
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "⚠️  You'll need to enter your GitHub credentials:" -ForegroundColor Yellow
Write-Host "   Username: Your GitHub username" -ForegroundColor White
Write-Host "   Password: Use a Personal Access Token (not your password)" -ForegroundColor White
Write-Host "   Create token at: https://github.com/settings/tokens" -ForegroundColor White
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "🌐 View your repository at: https://github.com/$username/$repoName" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Push failed. Please check the error message above." -ForegroundColor Red
    Write-Host "💡 Common issues:" -ForegroundColor Yellow
    Write-Host "   - Wrong username or repository name" -ForegroundColor White
    Write-Host "   - Need to use Personal Access Token instead of password" -ForegroundColor White
    Write-Host "   - Repository already has content (use 'git pull' first)" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
