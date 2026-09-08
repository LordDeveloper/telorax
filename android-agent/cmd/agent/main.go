package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/LordDeveloper/telorax/android-agent/internal/agent"
	"github.com/LordDeveloper/telorax/android-agent/internal/config"
	"github.com/LordDeveloper/telorax/android-agent/internal/telegram"
)

func main() {
	cfg := config.FromEnv()
	if err := cfg.Valid(); err != nil {
		log.Fatalf("config: %v", err)
	}

	runtime, err := agent.NewRuntime(cfg)
	if err != nil {
		log.Fatalf("runtime: %v", err)
	}

	runtime.SetCapabilities(telegram.Evaluate(false, true, false, false, "desktop smoke test"))

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	message, err := runtime.Bootstrap(ctx)
	if err != nil {
		log.Fatalf("bootstrap: %v", err)
	}
	fmt.Println(message)
	fmt.Printf("wireguard config bytes=%d telegram_ready=%t\n", len(runtime.WireGuardConfig()), runtime.TelegramReady())

	if err := runtime.RunHeartbeatLoop(ctx, 15*time.Second, func(status string) {
		fmt.Printf("heartbeat: %s\n", status)
	}); err != nil && err != context.Canceled {
		log.Fatalf("heartbeat loop: %v", err)
	}
}
