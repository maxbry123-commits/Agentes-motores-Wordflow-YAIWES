# VLM Chat Helper - Build Instructions

A desktop assistant for the GLM series multimodal models (GLM-4.5V, compatible with GLM-4.1V), supporting interactive conversations in multiple formats including text, images, videos, PDFs, and PPTs.
By connecting to the GLM multimodal API, it enables intelligent services across various scenarios.
The [installer](https://huggingface.co/spaces/zai-org/GLM-4.5V-Demo-App) is ready for direct use.

## Application Screenshots

![main](docs/images/main-interface.png)
![Floating Window Mode](docs/images/floating-window.png)
![setting](docs/images/settings.png)

## Special Notes

- The current version **only supports macOS Apple Silicon (M-series chips: M1/M2/M3, etc.)**
- Versions for Intel Macs, Windows, and Linux are not currently available.

---

## macOS Security Restriction Notice

When you first run an application downloaded on macOS, you may see a message saying “App is damaged” or “Cannot be opened.” This happens because macOS assigns a security quarantine attribute to downloaded files.
If you trust the source of the application, you can remove the quarantine attribute using the following command:

```bash
xattr -rd com.apple.quarantine /Applications/vlm-helper.app
```

## Main Features

- 🤖 **Multimodal Chat**: Supports intelligent conversations with text, images, videos, PDFs, and PPT files
- 📸 **Screenshot**: Quick full/region screenshots with a global hotkey
- 🎥 **Screen Recording**: Full-screen and region recording with automatic video compression
- 🪟 **Floating Window Mode**: Compact floating chat window for use anytime, anywhere
- 🎨 **Themes**: Multiple built-in code highlighting themes
- 📱 **Drag-and-Drop Upload**: Drag files directly into the chat interface
- ⌨️ **Hotkeys**: Rich set of global hotkeys
- 💾 **Local Storage**: Chat history stored in a local database

## Tech Stack

- **Front-end Framework**: Vue 3 + TypeScript
- **Desktop Runtime**: Electron
- **UI Component Library**: Naive UI
- **CSS Framework**: UnoCSS
- **Database**: Better-SQLite3
- **Build Tooling**: Electron Vite
- **Package Manager**: pnpm

## System Requirements

- **Node.js**: >= 18.0.0
- **pnpm**: >= 8.0.0
- **Operating System**: Windows 10+, macOS 10.15+, Ubuntu 18.04+

## Quick Start

### 1) Install dependencies

```bash
pnpm install
```

### 2) Run in development mode

```bash
pnpm dev
```

### 3) Build the application

```bash
# Build all platforms
pnpm build

# Build Windows
pnpm build:win

# Build macOS
pnpm build:mac

# Build Linux
pnpm build:linux

# Build without packaging
pnpm build:unpack
```

## Project Structure

```
vlm-chat-helper/
├── src/
│   ├── main/                         # Main process code
│   │   ├── index.ts                  # Main process entry
│   │   ├── modules/                  # Feature modules
│   │   │   ├── windowManager.ts      # Window management
│   │   │   ├── shortcutManager.ts    # Global hotkeys
│   │   │   ├── recordingManager.ts   # Screen recording
│   │   │   └── ipcHandlers.ts        # IPC handlers
│   │   ├── services/                 # Service layer
│   │   │   └── database.ts           # Database service
│   │   └── utils/                    # Utilities
│   ├── preload/                      # Preload scripts
│   │   └── index.ts                  # Preload entry
│   └── renderer/                     # Renderer process code
│       └── src/
│           ├── App.vue               # Root component
│           ├── main.ts               # Renderer entry
│           ├── components/           # Shared components
│           ├── views/                # Pages / views
│           ├── stores/               # State management
│           ├── composables/          # Composable utilities
│           └── utils/                # Utilities
├── build/                            # Build assets
├── resources/                        # App resources
├── package.json                      # Project config
├── electron.vite.config.ts           # Electron Vite config
└── electron-builder.yml              # Packaging config
```

## Configuration

### FFmpeg

The app uses FFmpeg for video compression. The `ffmpeg-static-electron` package is bundled, so no separate installation is required.

### Database

The app uses **Better-SQLite3** as the local database. The data file is automatically created in the user data directory.

## Development Commands

```bash
# Install dependencies
pnpm install

# Development mode
pnpm dev

# Type checking
pnpm typecheck

# Lint
pnpm lint

# Format code
pnpm format

# Rebuild native modules
pnpm rebuild

# Build the project
pnpm build

# Build with type checking
pnpm build:with-typecheck
```

## Compatibility

This project currently supports **macOS Apple Silicon (M‑series)** chips only.
