# VHS tape file for Idea Miner CLI demo
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

Type "rm -f idea_miner.sqlite3 && idea-miner init-db"
Enter
Sleep 2s

# Run the pipeline
Type "idea-miner run -s SideProject -l 3 -p 3"
Enter
Sleep 30s

# Show completion
Sleep 3s
