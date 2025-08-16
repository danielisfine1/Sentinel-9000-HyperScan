.PHONY: start stop attach

SESSION_NAME=sentinel

start:
	tmux new-session -d -s $(SESSION_NAME) 'source venv/bin/activate && python sentinel_server.py'
	tmux split-window -h -t $(SESSION_NAME) 'source venv/bin/activate && python sentinel_runner.py'
	tmux select-pane -t 0
	tmux attach-session -t $(SESSION_NAME)

stop:
	-tmux kill-session -t $(SESSION_NAME)

attach:
	tmux attach-session -t $(SESSION_NAME)
