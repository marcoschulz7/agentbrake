# vhs tape for the AgentBrake demo GIF.
# Install vhs (https://github.com/charmbracelet/vhs), then from the repo root:
#   vhs demo/demo.tape        ->  writes demo/agentbrake.gif
#
# Assumes a venv at .venv with `agentbrake-sdk[langchain]` and `langchain`
# installed (see DEMO.md). The tape just runs the no-API-key example so the
# brake engages on a real LangGraph loop and stops it at step 3.

Output demo/agentbrake.gif

Set FontSize 18
Set Width 1100
Set Height 600
Set Padding 20
Set Theme "Catppuccin Mocha"
Set TypingSpeed 60ms

Type "python examples/langchain_quickstart.py"
Sleep 400ms
Enter
Sleep 3s
