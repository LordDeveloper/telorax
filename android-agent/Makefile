.PHONY: test bind-android

test:
	go test ./...

bind-android:
	go install golang.org/x/mobile/cmd/gomobile@latest
	gomobile init
	gomobile bind -target=android -o android/app/libs/teloraxagent.aar ./mobile
