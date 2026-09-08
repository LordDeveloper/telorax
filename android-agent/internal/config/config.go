package config

import (
	"os"
	"strconv"
	"strings"
)

type Config struct {
	BaseURL   string
	AgentID   string
	Token     string
	Version   string
	Platform  string
	Arch      string
	UserAgent string
}

func FromEnv() Config {
	return Config{
		BaseURL:   strings.TrimRight(getenv("TELORAX_BASE_URL", "http://127.0.0.1:8000"), "/"),
		AgentID:   getenv("TELORAX_AGENT_ID", ""),
		Token:     getenv("TELORAX_AGENT_TOKEN", ""),
		Version:   getenv("TELORAX_AGENT_VERSION", "0.1.0"),
		Platform:  getenv("TELORAX_AGENT_PLATFORM", "android"),
		Arch:      getenv("TELORAX_AGENT_ARCH", "arm64"),
		UserAgent: getenv("TELORAX_AGENT_USER_AGENT", "telorax-android-agent/0.1.0"),
	}
}

func (c Config) Valid() error {
	if c.BaseURL == "" {
		return errf("base URL is required")
	}
	if c.AgentID == "" {
		return errf("agent id is required")
	}
	if c.Token == "" {
		return errf("agent token is required")
	}
	return nil
}

func getenv(key, fallback string) string {
	if value := strings.TrimSpace(os.Getenv(key)); value != "" {
		return value
	}
	return fallback
}

func ParseInt(value string, fallback int) int {
	parsed, err := strconv.Atoi(strings.TrimSpace(value))
	if err != nil {
		return fallback
	}
	return parsed
}

type configError string

func (e configError) Error() string { return string(e) }

func errf(message string) error { return configError(message) }
