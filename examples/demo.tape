# VHS tape file for Pain Radar CLI demo
# https://github.com/charmbracelet/vhs

Output examples/demo.gif

Set Shell "zsh"
Set FontSize 14
Set Width 1000
Set Height 600
Set Padding 20

# Setup
Type "source .venv/bin/activate"
Enter
Sleep 500ms

# Clean start
Type "rm -f pain_radar.sqlite3 && pain-radar init-db"
Enter
Sleep 2s

# Show version
Type "pain-radar --version"
Enter
Sleep 1s

# Fetch posts
Type "pain-radar fetch -s SideProject -l 5"
Enter
Sleep 8s

# Show stats
Type "pain-radar stats"
Enter
Sleep 2s

# Create a watchlist
Type 'pain-radar alerts-add "saas, startup" --name "SaaS Pain"'
Enter
Sleep 2s

# List watchlists
Type "pain-radar alerts"
Enter
Sleep 2s

# Show help
Type "pain-radar --help"
Enter
Sleep 3s
