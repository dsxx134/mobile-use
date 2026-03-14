# mobile-use: automate your phone with natural language

<div align="center">

![mobile-use in Action](./doc/banner-v2.png)

</div>

<div align="center">

[![Discord](https://img.shields.io/discord/1403058278342201394?color=7289DA&label=Discord&logo=discord&logoColor=white&style=for-the-badge)](https://discord.gg/6nSqmQ9pQs)
[![GitHub stars](https://img.shields.io/github/stars/minitap-ai/mobile-use?style=for-the-badge&color=e0a8dd)](https://github.com/minitap-ai/mobile-use/stargazers)

<h3>
    <a href="https://platform.mobile-use.ai"><b>☁️ Cloud</b></a> •
    <a href="https://docs.minitap.ai/v2/mcp-server/introduction"><b>📚 Documentation</b></a> •
    <a href="https://arxiv.org/abs/2602.07787"><b>📃 Paper</b></a>

</h3>
<p align="center">
    <a href="https://discord.gg/6nSqmQ9pQs"><b>Discord</b></a> •
    <a href="https://x.com/minitap_ai?t=iRWtI497UhRGLeCKYQekig&s=09"><b>Twitter / X</b></a>
</p>

[![PyPI version](https://img.shields.io/pypi/v/minitap-mobile-use.svg?color=blue)](https://pypi.org/project/minitap-mobile-use/)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](https://github.com/minitap-ai/mobile-use/blob/main/LICENSE)

</div>

Mobile-use is a powerful, open-source AI agent that controls your Android or IOS device using natural language. It understands your commands and interacts with the UI to perform tasks, from sending messages to navigating complex apps.

> Mobile-use is quickly evolving. Your suggestions, ideas, and reported bugs will shape this project. Do not hesitate to join in the conversation on [Discord](https://discord.gg/6nSqmQ9pQs) or contribute directly, we will reply to everyone! ❤️

## ✨ Features

- 🗣️ **Natural Language Control**: Interact with your phone using your native language.
- 📱 **UI-Aware Automation**: Intelligently navigates through app interfaces (note: currently has limited effectiveness with games as they don't provide accessibility tree data).
- 📊 **Data Scraping**: Extract information from any app and structure it into your desired format (e.g., JSON) using a natural language description.
- 🔧 **Extensible & Customizable**: Easily configure different LLMs to power the agents that power mobile-use.

## Benchmarks

<p align="center">
  <a href="https://minitap.ai/benchmark">
    <img src="https://files.peachworlds.com/website/2b590171-669d-42ce-b4b5-ce6eae83a9d8/scorerank-140126.webp" alt="Project banner" />
  </a>
</p>

We stand as the top performers and the first to have completed 100% of the AndroidWorld benchmark.

Get more info about how we reached this milestone here: [Minitap Benchmark](https://minitap.ai/benchmark).

The official leaderboard is available [here](https://docs.google.com/spreadsheets/d/1cchzP9dlTZ3WXQTfYNhh3avxoLipqHN75v1Tb86uhHo/edit?pli=1&gid=0#gid=0).

Check out our research paper [here](https://arxiv.org/abs/2602.07787).

## 🚀 Getting Started

Ready to automate your mobile experience? Follow these steps to get mobile-use up and running.

### 🌐 From our Platform

Easiest way to get started is to use our Platform.
Follow our [Platform quickstart](https://docs.minitap.ai/mobile-use-sdk/platform-quickstart) to get started.

### 🛠️ From source

1.  **Set up Environment Variables:**
    Copy the example `.env.example` file to `.env` and add your API keys.

    ```bash
    cp .env.example .env
    ```

2.  **(Optional) Customize LLM Configuration:**
    To use different models or providers, create your own LLM configuration file.

    ```bash
    cp llm-config.override.template.jsonc llm-config.override.jsonc
    ```

    Then, edit `llm-config.override.jsonc` to fit your needs.

    You can also use local LLMs or any other openai-api compatible providers :

    1. Set `OPENAI_BASE_URL` and `OPENAI_API_KEY` in your `.env`
    2. In your `llm-config.override.jsonc`, set `openai` as the provider for the agent nodes you want, and choose a model supported by your provider.

    > [!NOTE]
    > If you want to use Google Vertex AI, you must either:
    >
    > - Have credentials configured for your environment (gcloud, workload identity, etc…)
    > - Store the path to a service account JSON file as the GOOGLE_APPLICATION_CREDENTIALS environment variable
    >
    > More information: - [Credential types](https://cloud.google.com/docs/authentication/application-default-credentials#GAC) - [google.auth API reference](https://googleapis.dev/python/google-auth/latest/reference/google.auth.html#module-google.auth)

### Quick Launch (Docker)

> [!NOTE]
> This quickstart, is only available for Android devices/emulators as of now, and you must have Docker installed.

First:

- Either plug your Android device and enable USB-debugging via the Developer Options
- Or launch an Android emulator

Then run in your terminal:

1. For Linux/macOS:

```bash
chmod +x mobile-use.sh
bash ./mobile-use.sh \
  "Open Gmail, find first 3 unread emails, and list their sender and subject line" \
  --output-description "A JSON list of objects, each with 'sender' and 'subject' keys"
```

2. For Windows (inside a Powershell terminal):

```powershell
powershell.exe -ExecutionPolicy Bypass -File mobile-use.ps1 `
  "Open Gmail, find first 3 unread emails, and list their sender and subject line" `
  --output-description "A JSON list of objects, each with 'sender' and 'subject' keys"
```

> [!NOTE]
> If using your own device, make sure to accept the ADB-related connection requests that will pop up on your device.

#### 🧰 Troubleshooting

The script will try to connect to your device via IP.
Therefore, your device **must be connected to the same Wi-Fi network as your computer**.

##### 1. No device IP found

If the script fails with the following message:

```
Could not get device IP. Is a device connected via USB and on the same Wi-Fi network?
```

Then it couldn't find one of the common Wi-Fi interfaces on your device.
Therefore, you must determine what WLAN interface your phone is using via `adb shell ip addr show up`.
Then add the `--interface <YOUR_INTERFACE_NAME>` option to the script.

##### 2. Failed to connect to <DEVICE_IP>:5555 inside Docker

This is most probably an issue with your firewall blocking the connection. Therefore there is no clear fix for this.

##### 3. Failed to pull GHCR docker images (unauthorized)

Since UV docker images rely on a `ghcr.io` public repositories, you may have an expired token if you used `ghcr.io` before for private repositories.
Try running `docker logout ghcr.io` and then run the script again.

### Manual Launch (Development Mode)

For developers who want to set up the environment manually:

#### 1. Device Support

Mobile-use currently supports the following devices:

- **Physical Android Phones**: Connect via USB with USB debugging enabled.
- **Android Simulators**: Set up through Android Studio.
- **iOS Simulators**: Supported for macOS users.

> [!NOTE]
> Physical iOS devices are not yet supported.

#### 2. Prerequisites

**For Android:**

- **[Android Debug Bridge (ADB)](https://developer.android.com/studio/releases/platform-tools)**: A tool to connect to your device.

**For iOS (macOS only):**

- **[Xcode](https://developer.apple.com/xcode/)**: Apple's IDE for iOS development.
- **[fb-idb](https://fbidb.io/docs/installation/)**: Facebook's iOS Development Bridge for device automation.

  ```bash
  # Install via Homebrew (macOS)
  brew tap facebook/fb
  brew install idb-companion
  ```

  > [!NOTE]
  > `idb_companion` is required to communicate with iOS simulators. Make sure it's in your PATH after installation.

**Common requirements:**

Before you begin, ensure you have the following installed:

- **[uv](https://github.com/astral-sh/uv)**: A lightning-fast Python package manager.

#### 3. Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/minitap-ai/mobile-use.git && cd mobile-use
    ```

2.  [**Setup environment variables**](#-getting-started)

3.  **Create & activate the virtual environment:**

    ```bash
    # This will create a .venv directory using the Python version in .python-version
    uv venv

    # Activate the environment
    # On macOS/Linux:
    source .venv/bin/activate
    # On Windows:
    .venv\Scripts\activate
    ```

4.  **Install dependencies:**
    ```bash
    # Sync with the locked dependencies for a consistent setup
    uv sync
    ```

## 👨‍💻 Usage

To run mobile-use, simply pass your command as an argument.

**Example 1: Basic Command**

```bash
uv run mobile-use "Go to settings and tell me my current battery level"
```

**Example 2: Data Scraping**

Extract specific information and get it back in a structured format. For instance, to get a list of your unread emails:

```bash
uv run mobile-use \
  "Open Gmail, find all unread emails, and list their sender and subject line" \
  --output-description "A JSON list of objects, each with 'sender' and 'subject' keys"
```

> [!NOTE]
> If you haven't configured a specific model, mobile-use will prompt you to choose one from the available options.

## Android Debug MCP

The repository also ships a local Android debugging MCP server for device inspection and
automation debugging. It reuses the same `adbutils` and `UIAutomatorClient` stack as the
main Android controller, so debug snapshots stay aligned with production automation.

### Requirements

- `adb` available in your `PATH`
- A connected Android device or emulator
- Optional: `scrcpy` for live mirroring while debugging
- Optional: `uiautodev` for independent hierarchy inspection

### Start the MCP server

```bash
uv run mobile-use-android-debug-mcp
```

### Smoke test the local setup

```bash
uv run python scripts/android_debug_mcp_smoke.py
```

### Intended use

- Debug Android UI flows before encoding them into deterministic automations
- Inspect screenshots, hierarchy XML, and foreground app state from one MCP endpoint
- Support Xianyu publishing automation with a repo-local Android debugging toolchain

## Xianyu Publish Foundation

This branch also includes the first business-layer foundation for Xianyu publishing. It does
not submit listings inside the Xianyu app yet. Instead, it now covers the upstream data/media
pipeline plus the first deterministic in-app publish navigation layer.

### What is implemented

- `feishu_source`: reads candidate listing records from Feishu Bitable and normalizes them into
  a `ListingDraft`
- `media_sync`: downloads Feishu attachment assets into a local staging directory and pushes them
  onto an Android device directory through `adbutils`
- `flow`: recognizes key Xianyu publish screens and can deterministically advance from the
  Xianyu home tab into the portrait listing form, metadata panel, album picker, description
  editor, sale-price panel, and shipping panel

### Deterministic flow coverage

- Recovers the app with an explicit Xianyu main-activity launch instead of relying on the generic
  package launcher
- Recognizes:
  - Xianyu home tab
  - publish chooser
  - portrait listing form
  - expanded metadata/spec panel
  - description editor
  - sale-price keypad panel
  - shipping bottom sheet
  - Android media permission dialog
  - album picker
  - album source menu
  - post-confirm photo analysis screen
  - the `宝贝` empty-state page inside Xianyu space
- Can:
  - tap `卖闲置`
  - tap `发闲置`
  - force the Huawei tablet into portrait mode before entering the real publish form
  - continue through the draft-resume dialog when `发闲置` reopens an unfinished listing
  - poll through the post-`继续` tail until the dialog really clears
  - extract the portrait publish-form targets from real-device `content-desc` semantics
  - enter the dedicated description editor from the portrait form
  - fill description text and return to the portrait form
  - open the sale-price bottom sheet from the portrait form
  - clear and enter a sale price through the on-screen keypad
  - confirm the price and return to the portrait form
  - open the shipping bottom sheet from the portrait form
  - switch between verified mail shipping modes and return to the portrait form
  - open the root location chooser from the portrait form
  - enter the hierarchical location region picker by tapping `请选择宝贝所在地`
  - open the dedicated location search screen from `宝贝所在地`
  - fill the focused address search field with direct `EditText.set_text()`
  - tap a visible location search result row and return to the next Xianyu screen
  - expand the portrait form into the metadata/spec panel
  - set a currently visible category chip from the metadata/spec panel
  - set the verified `成色` chip options
  - set the verified `商品来源` chip options
  - accept the media permission dialog
  - reopen the album picker directly from the portrait form by tapping `添加图片`
  - switch the album source to a dedicated folder like `XianyuPublish`
  - select one image and confirm it
  - continue through image preview and image edit screens back into the form
  - bridge from the Xianyu space analysis flow back into the standard publish chooser
  - run a deterministic `XianyuPrepareRunner` that prepares one publishable Bitable record into the form with media, merged title+description body, and price

### Required environment variables

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `XIANYU_BITABLE_APP_TOKEN`
- `XIANYU_BITABLE_TABLE_ID`
- Optional: `XIANYU_ANDROID_MEDIA_DIR` (defaults to `/sdcard/DCIM/XianyuPublish`)

### Default Bitable field mapping

- `商品标题`
- `商品描述`
- `售价`
- `分类`
- `成色`
- `商品来源`
- `商品图片`
- `发布状态`
- `是否允许发布`

### Smoke test the foundation settings

```bash
uv run python scripts/xianyu_publish_foundation_smoke.py
```

### Smoke test the current Xianyu screen recognizer

```bash
uv run python scripts/xianyu_publish_flow_smoke.py
```

### Current media-selection behavior

- The preferred publish path on the Huawei tablet is now portrait mode:
  - force portrait
  - tap `卖闲置`
  - tap `发闲置`
  - if Xianyu has an unfinished draft, tap `继续`
  - land on the standard listing form
- On the real portrait form, key controls such as `发布`, `添加图片`, and the large description tile
  are exposed through `content-desc` values like `发布, 发布` and `描述, 描述一下宝贝的品牌型号、货品来源…`
- On this Huawei tablet, tapping `发闲置` does not always enter the form directly; an unfinished
  draft can surface a blocking dialog with `放弃` and `继续`, and the deterministic path is to tap
  `继续`
- After tapping `继续`, the dialog can linger for one or two snapshots; the flow now polls until
  that tail clears instead of tapping `继续` twice
- The description path now uses a dedicated editor state with a `完成` control
- On this Huawei tablet, `input_text()` can already return from that editor back to `listing_form`;
  the flow now detects that and avoids stale `完成` taps that can accidentally open `价格设置`
- The portrait form also exposes a tappable `价格设置` row; on the Huawei tablet it opens a
  dedicated bottom-sheet keypad with `删除`, `确定`, and digit targets rather than a text IME
- Sale price entry is now deterministic:
  - tap `价格设置`
  - clear the previous value with `删除`
  - tap digits plus `.` on the keypad
  - tap `确定`
  - wait until the portrait form is visible again
- Real-device verification confirmed that entering `399.9` through the keypad returns to
  `listing_form` and renders the price row as `¥399.90`
- The portrait form also exposes a `发货方式` row; on the Huawei tablet it opens a bottom-sheet
  selector with a multiline `邮寄` block plus left-side radio icons for the mail modes
- Shipping selection is now deterministic for the verified mail modes:
  - `包邮`
  - `不包邮-按距离付费`
  - `不包邮-固定邮费`
  - `无需邮寄`
- On this Huawei tablet, tapping the multiline mail text is not enough; the actual selectable
  targets are the left-side radio icons
- After tapping `确定`, the shipping panel can briefly linger or collapse into a status-only
  `unknown` overlay before the portrait form returns; the flow now polls through both transitions
- `买家自提` is still outside the deterministic support set for now because its visible text target
  did not prove reliably selectable during real-device probing
- The portrait form also exposes a `选择位置` row; the flow now recognizes both the root
  `宝贝所在地` chooser and the hierarchical `所在地` region picker
- The location bridge also works from a scrolled `metadata_panel` state when the lower
  `选择位置` row is visible on screen
- The root `宝贝所在地` chooser also exposes a dedicated `搜索地址` path
- On this Huawei tablet, that search page does not reliably accept the existing FastInputIME
  `send_keys()` path even though the field is focused
- Real-device probing showed that the screen exposes a focused `android.widget.EditText` with
  `hint="搜索地址"`, and using direct `EditText.set_text()` is what actually surfaces visible
  result rows such as `上海虹桥站\n新虹街道申贵路1500号`
- The flow now treats that page as `location_search_screen` and can:
  - tap `搜索地址`
  - set text on the focused field
  - tap a visible result row
  - return to the next Xianyu screen
- The stable path into region selection is:
  - tap `选择位置`
  - wait for `宝贝所在地`
  - tap the full `请选择宝贝所在地` row
  - enter the `所在地` region picker
- Real-device probing also showed that selecting a top-level region such as `上海` does not yet
  finish location selection; it narrows the same hierarchical picker and still needs another step
- After the final district tap, the app can briefly keep the `location_region_picker` overlay
  visible on top of the listing form before it settles. The flow now polls through that tail
  instead of treating the first post-tap frame as a hard failure.
- Final location writeback is still not treated as deterministic yet; real-device probing did not
  produce a stable, visible confirmation on the listing form after selecting either a common
  address row, a search result row, or a region row
- The portrait form also exposes a large metadata section row such as `分类/ISBN码/成色` or
  richer variants like `分类/盒袋状态/盒卡状态/等\n款式`
- On the Huawei tablet, expanding that row does not open the old publish chooser; it opens a
  stable metadata/spec page that still shows the main `发闲置` header plus chip-style options
- The flow now treats that state as `metadata_panel` instead of misclassifying it as
  `publish_chooser`
- A scrolled editor state can still belong to the same `metadata_panel` even when upper-form
  controls like `添加图片` are no longer visible, as long as metadata chips plus lower rows such as
  `价格设置`, `发货方式`, or `选择位置` remain on screen
- Real-device verification confirmed that tapping a chip such as `几乎全新` changes the visible
  text from `可选几乎全新, 几乎全新` to `已选中几乎全新, 几乎全新`
- The currently verified deterministic metadata fields are:
  - visible `分类` chips on the current metadata panel, such as `家居摆件` and `生活百科`
  - `成色`: `全新`, `几乎全新`, `轻微使用痕迹`, `明显使用痕迹`
  - `商品来源`: `盒机转赠`, `盒机直发`, `淘宝转卖`, `闲置`
- Category support in this branch is intentionally limited to the chips already visible on the
  expanded metadata panel; it does not yet drive a deeper category tree or search flow
- From that portrait form, tapping `添加图片` opens the album picker directly without going back
  through the older publish chooser path
- On the current app build, image selection can continue through extra media-processing screens:
  - `selected_media_preview` with `下一步 (1)`
  - `media_edit_screen` with tools like `裁剪` and a `完成` button
- On the Huawei tablet, tapping `完成` on that media edit screen can return directly to
  `listing_form`, sometimes with auto-filled metadata rows like `分类` or `ISBN码`
- On a fresh device session, the first FastInputIME text entry can trigger a one-time
  `com.github.uiautomator/.AdbKeyboard` installation and briefly switch foreground away from Xianyu;
  after that warm-up, subsequent text entry is stable
- For deterministic selection, push listing images into a dedicated device folder such as
  `XIANYU_ANDROID_MEDIA_DIR=/sdcard/DCIM/XianyuPublish`
- The flow can switch the picker from `所有文件` into `XianyuPublish` before tapping `选择`
- After tapping `确定`, real devices can briefly linger on an album-picker tail state that still
  shows `预览 (1)` and `确定`; the flow now polls until that transient state clears
- Once the tail state clears, the current app version lands on a `photo_analysis` screen before
  any final listing form appears
- On recognizable product images, that `photo_analysis` screen can surface a detected-item branch
  such as `1个宝贝` plus a computed price range, but the automation still does not advance into
  the final edit form yet
- On the Huawei tablet, the Xianyu space flow is partly visual-only: dismissing the analysis
  overlay and tapping the `发宝贝` button currently use normalized ratio taps rather than
  accessibility targets
- The flow can now bridge `photo_analysis -> 宝贝空态页 -> 发宝贝 -> 发布选择器`, which gives the
  automation a deterministic way to escape the space overlay back into the standard chooser
- The older landscape space-analysis path is still useful for investigation, but it is no longer
  the preferred way to reach the publish form
- The current app/device pair does not expose a separate title input on the portrait `发闲置` form,
  so the prepare runner folds `ListingDraft.title` into the description body as the first line,
  followed by a blank line and the original description text when needed

### Current prepare-runner behavior

- `XianyuPrepareRunner` currently orchestrates the deterministic business slice:
  - pick the first publishable Bitable record
  - resolve temporary download URLs for attachments
  - download staged media into a record-scoped local directory
  - push the staged files into `XIANYU_ANDROID_MEDIA_DIR/<record_id>`
  - reach the portrait listing form
  - reopen the album picker
  - switch to `XianyuPublish`
  - select the first prepared image
  - if needed, bridge back from `photo_analysis` into the portrait form
  - fill the merged title+description body
  - fill the sale price
  - optionally apply a visible category chip
  - optionally apply `成色`
  - optionally apply `商品来源`
- Real-device verification on `E2P6R22708000602` confirmed a full prepare-runner pass that ended
  on `listing_form` with body text and price filled
- Real-device verification also confirmed that the current metadata page is recognized as
  `metadata_panel`, and that `set_item_condition('几乎全新')` and `set_item_source('闲置')`
  both end on visible selected-chip states
- A fresh real-device probe also confirmed that `set_item_category('生活百科')` stays on
  `metadata_panel` and flips the selected category target from `家居摆件` to `生活百科`
- The runner intentionally stops once the form is prepared and visible again; it does not yet claim:
  - category selection
  - stable location persistence
  - shipping writeback from Bitable
  - final publish submission

### Current boundary

- The flow can now reach the portrait listing form, fill description text, set the sale price,
  set the verified mail shipping mode, set verified metadata chips for
  `分类/成色/商品来源`,
  reopen the album picker from `添加图片`, and prepare one publishable Bitable record into the
  form through `XianyuPrepareRunner`
- When the editor is scrolled into the metadata section, the flow now keeps that state classified
  as `metadata_panel` and can still open `价格设置`, `发货方式`, and `选择位置` from it
- Stable location persistence, deeper category navigation, `买家自提`, and final publish
  submission are still the next layer
- The location search helper can now drive the dedicated search UI and visible result rows, but it
  still returns to a form whose visible location row remains `选择位置`

## 🔎 Agentic System Overview

<div align="center">

![Graph Visualization](doc/graph.png)

_This diagram is automatically updated from the codebase. This is our current agentic system architecture._

</div>

## ❤️ Contributing

We love contributions! Whether you're fixing a bug, adding a feature, or improving documentation, your help is welcome. Please read our **[Contributing Guidelines](CONTRIBUTING.md)** to get started.

## ⭐ Star History

<p align="center">
  <a href="https://star-history.com/#minitap-ai/mobile-use&Date">
    <img src="https://api.star-history.com/svg?repos=minitap-ai/mobile-use&type=Date" alt="Star History Chart" />
  </a>
</p>

## 🏆 Attribution & Licensing

`mobile-use` is the first agentic framework to achieve **100% on the AndroidWorld benchmark**.

This project is licensed under the **Apache License 2.0**.

If you use this code, or are inspired by the architecture used to reach our benchmark results, we kindly request that you credit Minitap, Inc.

### How to Cite
If you use this work in research or a commercial product, please use the following:
> Pierre-Louis Favreau, Jean-Pierre Lo, Clement Guiguet, Charles Simon-Meunier,  
Nicolas Dehandschoewercker, Allen G. Roush, Judah Goldfeder, Ravid Shwartz-Ziv.  
_Do Multi-Agents Dream of Electric Screens? Achieving Perfect Accuracy on AndroidWorld Through Task Decomposition._  
arXiv preprint arXiv:2602.07787 (2026).  
https://arxiv.org/abs/2602.07787

#### Bibtex


```bibtex
@misc{favreau2026multiagentsdreamelectricscreens,
  title        = {Do Multi-Agents Dream of Electric Screens? Achieving Perfect Accuracy on AndroidWorld Through Task Decomposition},
  author       = {Pierre-Louis Favreau and Jean-Pierre Lo and Clement Guiguet and Charles Simon-Meunier and Nicolas Dehandschoewercker and Allen G. Roush and Judah Goldfeder and Ravid Shwartz-Ziv},
  year         = {2026},
  eprint       = {2602.07787},
  archivePrefix= {arXiv},
  primaryClass = {cs.AI},
  url          = {https://arxiv.org/abs/2602.07787}
}

