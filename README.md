<div align="center">

<img src="docs/images/icon.png" alt="" width="72"/>

# Language Profile Switcher

**Switch your Windows keyboard languages between profiles in one click, without a reboot.**

[![Latest release](https://img.shields.io/github/v/release/Maxkii3/LangProfileSwitcher?style=flat-square&color=ff385c)](https://github.com/Maxkii3/LangProfileSwitcher/releases/latest)
[![License: All rights reserved](https://img.shields.io/badge/license-All%20rights%20reserved-222222?style=flat-square)](LICENSE)
[![Platform: Windows 10 | 11](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D4?style=flat-square&logo=windows&logoColor=white)](#installation)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6 / Qt 6](https://img.shields.io/badge/PySide6-Qt%206-41CD52?style=flat-square&logo=qt&logoColor=white)](https://doc.qt.io/qtforpython-6/)

**[Download the installer](https://github.com/Maxkii3/LangProfileSwitcher/releases/latest)** ·
[Install](#installation) ·
[Usage](#usage) ·
[Report a bug](https://github.com/Maxkii3/LangProfileSwitcher/issues)

🌐 **English** · [ภาษาไทย](#thai)

</div>

---

<a name="support"></a>
## ❤️ Support & Sponsor

Language Profile Switcher is free. If it saves you a few annoying keyboard cycles a day, you can support
its development.<br>
แอปนี้ใช้ฟรี ถ้าช่วยให้การสลับภาษาของคุณง่ายขึ้น สามารถสนับสนุนการพัฒนาได้ผ่านช่องทางด้านล่าง

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Donate-yellow?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/maxkii3)
[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-Sponsor-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/Maxkii3)

<div align="center">
  <a href="https://www.gsttopup.com/shop" target="_blank">
    <img src="docs/images/gst_topup_logo.png" alt="GST Topup" width="280"/>
  </a>
  <br/>
  <sub>🎮 <b>Sponsored by / สนับสนุนโดย:</b> <a href="https://www.gsttopup.com/shop">GST Topup</a></sub>
  <br/>
  <sub><b>TH:</b> เติมเกมถูก รวดเร็ว ปลอดภัย แนะนำที่ GST Topup | <b>EN:</b> Affordable, fast, and secure game top-ups at GST Topup</sub>
</div>

Bug reports and ideas are welcome in [Issues](https://github.com/Maxkii3/LangProfileSwitcher/issues). A ⭐ on the
repo helps other people find it too.

---

<a name="english"></a>
## The problem

Two people share one Windows PC. One of them types in **English, Thai, Chinese and Korean**; the other only
needs **English and Thai**. Windows keeps a single input-language list per account, so `Win+Space` /
`Alt+Shift` cycles through all four languages for both of them, and adding and removing languages in
Settings every time you swap seats takes minutes.

**Language Profile Switcher** keeps named profiles of that list (for example *Full* and *Minimal*) and swaps
between them from the system tray in about a second. No reboot, no sign-out, no admin rights.

## ✨ Features

- **Instant switching:** pick a profile in the tray menu, left-click the tray icon, or press
  **`Ctrl + Alt + L`** to toggle between your last two profiles.
- **Keyboards stay exactly as you set them:** each language keeps its own keyboard layouts and IMEs
  (Microsoft Pinyin, Microsoft IME, Thai Kedmanee and others), so a profile restores them exactly as they were.
- **Display-language protection:** Windows uses the first language in the list as its interface language.
  The app warns you when a profile would change it and fixes the order with one click.
- **Safe exit:** quitting while on a reduced profile asks whether to **revert to your default profile**
  first, so the next person isn't left with missing languages.
- **Active profile at a glance:** in the settings window the active profile is a raised card with a Rausch-red
  border and an *Active* badge, and a pointing hand marks it.
- **System tray app:** the tray icon shows the active profile's initial, it can start with Windows, and
  only one copy runs at a time.
- **Nothing bundled from the author's PC:** on first launch the app reads *your* installed languages
  and builds a **Full** profile (your default) and a **Minimal** profile (your first two languages) from them.
- **Private and offline:** no network access, no telemetry. Settings live in one JSON file on your PC.

<a name="screenshots"></a>
## 📸 Screenshots

<table>
  <tr>
    <td width="60%"><img src="docs/images/settings.png" alt="Settings window: profiles on the left, the selected profile's languages with checkboxes, keyboards and a Display language badge on the right"><br><sub><b>Manage profiles:</b> the hand points at the active profile. Tick the languages a profile cycles through, drag to reorder, and switch with one button.</sub></td>
    <td width="40%"><img src="docs/images/tray-menu.png" alt="Tray icons for Full, Minimal and switching states, and the tray menu with profiles, Settings and Exit"><br><sub><b>Tray:</b> the icon shows the active profile; right-click to switch, open settings, or exit.</sub></td>
  </tr>
  <tr>
    <td width="60%"><img src="docs/images/display-language-warning.png" alt="A warning banner: Windows display language may change, with a Put English first button"><br><sub><b>Display-language protection:</b> a one-click fix when a profile would change the Windows UI language.</sub></td>
    <td width="40%"><img src="docs/images/exit-prompt.png" alt="Exit prompt: revert to the default profile before exiting, with Revert and Exit, Exit without Reverting and Cancel"><br><sub><b>Safe exit:</b> offers to restore your default profile before quitting.</sub></td>
  </tr>
</table>

<a name="installation"></a>
## 📦 Installation

### Option A: installer (recommended)

1. Download **`LangProfileSwitcher-Setup.exe`** from the
   [latest release](https://github.com/Maxkii3/LangProfileSwitcher/releases/latest).
2. Run it. It installs for your Windows user only (no admin prompt) into
   `%LOCALAPPDATA%\Programs\LangProfileSwitcher` and adds a **Start Menu** shortcut, plus optional
   **Desktop** and **Start automatically when I sign in** shortcuts.
3. The settings window opens on the first launch. After that the app lives in the tray.

> **Windows SmartScreen:** the installer is not code-signed yet, so Windows may show *"Windows protected your
> PC"*. Click **More info → Run anyway**. Each release lists the installer's SHA-256 so you can verify the download.

**Uninstall:** *Settings → Apps → Installed apps → Language Profile Switcher*. Your profiles in
`%LOCALAPPDATA%\LangProfileSwitcher` are kept; delete that folder to remove them too. Uninstalling does not
change your language list, so switch to your default profile first if you're on a reduced one.

### Option B: run from source

```powershell
git clone https://github.com/Maxkii3/LangProfileSwitcher.git
cd LangProfileSwitcher
python -m pip install -r requirements.txt     # PySide6
python run.py                                 # --settings opens the window at start
```

Requires Windows 10/11 and Python 3.10+.

<a name="usage"></a>
## 🧭 Usage

| Action | How |
|---|---|
| Toggle last two profiles | Left-click the tray icon, or press **`Ctrl + Alt + L`** |
| Pick any profile | Right-click the tray icon → click a profile (✔ = active) |
| Create / rename / delete profiles | Right-click → **Settings / Manage Profiles** |
| Choose a profile's languages | Tick or untick them; **drag** (or *Move up / down / to top*) to reorder |
| Add a new Windows language | **Add language** opens *Windows Settings → Language & region*; it appears in the app when you come back |
| Set the fallback profile | **Make default**. Exit offers to revert to it |
| Quit | Right-click → **Exit** (closing the settings window only hides it) |

### Hotkey

The toggle hotkey defaults to **`Ctrl + Alt + L`**. To change it, open **Settings**, click the **Toggle hotkey**
field and press the new combination. Use **Ctrl**, **Alt** or **Win** plus a letter, digit or **F1–F24**
(for example `Ctrl + Alt + K` or `Win + F9`). Clear the field to turn the hotkey off; the tray icon still
toggles. If another app already owns the combination, the field tells you right away.

### Good to know

- **One Windows account:** the language list is per Windows user. The app is for people who share **one**
  account; separate accounts already have separate lists.
- **The first language is the display language.** Keep your Windows UI language at the top of every profile
  (the app warns you when it isn't).
- **Language packs:** Windows can remove language packs that no list uses for a while. Keyboards and IMEs are
  built in and stay, but optional extras (handwriting, speech) may need a re-download. To prevent this, run once
  in an admin PowerShell: `Disable-ScheduledTask -TaskPath '\Microsoft\Windows\MUI\' -TaskName LPRemove`.

## ⚙️ How it works

| Piece | Where |
|---|---|
| Reads the live list from `HKCU\Control Panel\International\User Profile` (instant, no PowerShell) | [`langprofile/winlang.py`](langprofile/winlang.py) |
| Writes it with `Set-WinUserLanguageList` in a hidden PowerShell on a worker thread, then re-reads to verify | [`langprofile/winlang.py`](langprofile/winlang.py) |
| Profiles, toggle rule, atomic JSON save (a corrupt file is moved aside, never overwritten) | [`langprofile/core.py`](langprofile/core.py) |
| Global hotkey via `RegisterHotKey` + a Qt native event filter | [`langprofile/hotkey.py`](langprofile/hotkey.py) |
| Tray, settings window, safe-exit flow | [`langprofile/app.py`](langprofile/app.py), [`langprofile/ui.py`](langprofile/ui.py) |

Config: `%LOCALAPPDATA%\LangProfileSwitcher\config.json` · errors: `error.log` in the same folder.

## 🛠️ Build from source

```powershell
python -m pip install -r requirements-dev.txt       # PySide6 + PyInstaller
winget install JRSoftware.InnoSetup                  # once, for the installer
.\build.ps1                                          # tests -> PyInstaller -> dist\LangProfileSwitcher-Setup.exe
python -m unittest discover -s tests                 # tests only
python tools\screenshots.py                          # re-render docs\images (demo data, touches nothing)
```

## 📄 License

© 2026 [Maxkii3](https://github.com/Maxkii3). **All rights reserved.** You may download the release, or run the
unmodified source, for personal use. Copying, modifying or redistributing the code needs the author's written
permission. See [LICENSE](LICENSE).

Language Profile Switcher is an independent tool, not affiliated with Microsoft. Windows is a trademark of
Microsoft Corporation.

---

<a name="thai"></a>
## 🇹🇭 ภาษาไทย

[English](#english) · **ภาษาไทย**

**สลับชุดภาษาแป้นพิมพ์ของ Windows ระหว่างโปรไฟล์ได้ในคลิกเดียว ไม่ต้องรีสตาร์ทเครื่อง**

### ปัญหาที่แอปนี้แก้

คนสองคนใช้คอมพิวเตอร์ Windows เครื่องเดียวกัน คนหนึ่งพิมพ์ **อังกฤษ ไทย จีน และเกาหลี** ส่วนอีกคนใช้แค่
**อังกฤษกับไทย** แต่ Windows เก็บรายการภาษาสำหรับป้อนข้อมูลไว้เพียงชุดเดียวต่อหนึ่งบัญชีผู้ใช้ ทุกครั้งที่กด
`Win+Space` หรือ `Alt+Shift` จึงต้องวนผ่านทั้งสี่ภาษา และการเข้าไปเพิ่มหรือลบภาษาใน Settings ทุกครั้งที่สลับคนใช้
ก็เสียเวลาหลายนาที

**Language Profile Switcher** เก็บรายการภาษาเหล่านั้นเป็นโปรไฟล์ที่ตั้งชื่อเองได้ (เช่น *Full* และ *Minimal*)
แล้วสลับระหว่างโปรไฟล์จากถาดระบบ (System Tray) ได้ในเวลาประมาณหนึ่งวินาที ไม่ต้องรีสตาร์ท ไม่ต้องออกจากระบบ
และไม่ต้องใช้สิทธิ์ผู้ดูแลระบบ

### ✨ ฟีเจอร์หลัก

- **สลับได้ทันที:** เลือกโปรไฟล์จากเมนูในถาดระบบ คลิกซ้ายที่ไอคอน หรือกด **`Ctrl + Alt + L`**
  เพื่อสลับไปมาระหว่างสองโปรไฟล์ล่าสุด
- **แป้นพิมพ์กลับมาเหมือนเดิมทุกครั้ง:** แต่ละภาษาจำรูปแบบแป้นพิมพ์และ IME ของตัวเองไว้
  (เช่น Microsoft Pinyin, Microsoft IME, Thai Kedmanee) และได้กลับมาแบบเดิมทุกครั้งที่สลับโปรไฟล์
- **ป้องกันภาษาหน้าจอเปลี่ยนโดยไม่ตั้งใจ:** Windows ใช้ภาษาแรกในรายการเป็นภาษาของเมนูและหน้าจอ
  แอปจะเตือนเมื่อโปรไฟล์ใดจะทำให้ภาษานี้เปลี่ยน และจัดลำดับให้ถูกต้องได้ในคลิกเดียว
- **ปิดแอปอย่างปลอดภัย:** ถ้าปิดแอปขณะใช้โปรไฟล์ที่มีภาษาน้อยกว่า แอปจะถามก่อนว่าจะ
  **กลับไปใช้โปรไฟล์หลัก (Default)** หรือไม่ คนที่ใช้เครื่องต่อจะได้ไม่เจอภาษาหายไป
- **เห็นโปรไฟล์ที่ใช้อยู่ได้ทันที:** ในหน้าตั้งค่า โปรไฟล์ที่ใช้งานอยู่จะเป็นการ์ดยกนูนขอบสีแดง มีป้าย *Active*
  และมีรูปมือชี้ไว้
- **อยู่ในถาดระบบ:** ไอคอนแสดงอักษรตัวแรกของโปรไฟล์ที่ใช้งานอยู่ ตั้งให้เปิดพร้อม Windows ได้
  และทำงานได้ทีละหนึ่งตัวเท่านั้น (เปิดซ้ำก็ไม่ซ้อนกัน)
- **ไม่มีข้อมูลจากเครื่องผู้พัฒนาติดมา:** เมื่อเปิดครั้งแรก แอปจะอ่านภาษาที่ติดตั้งอยู่ใน *เครื่องของคุณ*
  แล้วสร้างโปรไฟล์ **Full** (เป็นโปรไฟล์หลัก) และ **Minimal** (สองภาษาแรกของคุณ) ให้อัตโนมัติ
- **เป็นส่วนตัวและทำงานออฟไลน์:** ไม่เชื่อมต่ออินเทอร์เน็ต ไม่เก็บสถิติการใช้งาน
  การตั้งค่าทั้งหมดอยู่ในไฟล์ JSON ไฟล์เดียวบนเครื่องของคุณ

ดูภาพหน้าจอได้ที่ [Screenshots](#screenshots) ด้านบน

### 📦 การติดตั้ง

#### วิธี A: ใช้ตัวติดตั้ง (แนะนำ)

1. ดาวน์โหลด **`LangProfileSwitcher-Setup.exe`** จาก
   [รีลีสล่าสุด](https://github.com/Maxkii3/LangProfileSwitcher/releases/latest)
2. เปิดไฟล์เพื่อติดตั้ง โปรแกรมจะติดตั้งเฉพาะบัญชีผู้ใช้ของคุณ (ไม่ขอสิทธิ์ผู้ดูแลระบบ) ไว้ที่
   `%LOCALAPPDATA%\Programs\LangProfileSwitcher` และสร้างทางลัดใน **Start Menu**
   พร้อมตัวเลือกสร้างทางลัดบน **Desktop** และ **เปิดอัตโนมัติเมื่อลงชื่อเข้าใช้ Windows**
3. หน้าตั้งค่าจะเปิดขึ้นในครั้งแรก หลังจากนั้นแอปจะทำงานอยู่ในถาดระบบ

> **Windows SmartScreen:** ตัวติดตั้งยังไม่ได้ลงลายเซ็นดิจิทัล (code-signing) Windows จึงอาจแสดงข้อความ
> *"Windows protected your PC"* ให้คลิก **More info → Run anyway** ทุกรีลีสมีค่า SHA-256 ของตัวติดตั้ง
> ไว้ตรวจสอบไฟล์ที่ดาวน์โหลดมา

**ถอนการติดตั้ง:** *Settings → Apps → Installed apps → Language Profile Switcher* โปรไฟล์ของคุณใน
`%LOCALAPPDATA%\LangProfileSwitcher` จะยังอยู่ (ลบโฟลเดอร์นี้หากต้องการลบโปรไฟล์ด้วย)
การถอนการติดตั้งไม่เปลี่ยนรายการภาษา ถ้ากำลังใช้โปรไฟล์ที่มีภาษาน้อย ให้สลับกลับไปโปรไฟล์หลักก่อน

#### วิธี B: รันจากซอร์สโค้ด

```powershell
git clone https://github.com/Maxkii3/LangProfileSwitcher.git
cd LangProfileSwitcher
python -m pip install -r requirements.txt     # PySide6
python run.py                                 # --settings = เปิดหน้าตั้งค่าตอนเริ่ม
```

ต้องใช้ Windows 10/11 และ Python 3.10 ขึ้นไป

### 🧭 วิธีใช้งาน

| ต้องการ | วิธีทำ |
|---|---|
| สลับระหว่างสองโปรไฟล์ล่าสุด | คลิกซ้ายที่ไอคอนในถาดระบบ หรือกด **`Ctrl + Alt + L`** |
| เลือกโปรไฟล์ใดก็ได้ | คลิกขวาที่ไอคอน → คลิกชื่อโปรไฟล์ (✔ = กำลังใช้งาน) |
| สร้าง / เปลี่ยนชื่อ / ลบโปรไฟล์ | คลิกขวา → **Settings / Manage Profiles** |
| เลือกภาษาของโปรไฟล์ | ติ๊กหรือเอาติ๊กออก แล้ว **ลาก** (หรือใช้ *Move up / Move down / Move to top*) เพื่อจัดลำดับ |
| เพิ่มภาษาใหม่ให้ Windows | ปุ่ม **Add language** จะเปิด *Windows Settings → Language & region* เมื่อกลับมาที่แอป ภาษาใหม่จะขึ้นมาเอง |
| ตั้งโปรไฟล์หลัก | **Make default** ตอนปิดแอปจะมีตัวเลือกให้กลับไปใช้โปรไฟล์นี้ |
| ปิดโปรแกรม | คลิกขวา → **Exit** (การปิดหน้าต่างตั้งค่าเป็นแค่การซ่อน แอปยังทำงานอยู่) |

#### คีย์ลัด

คีย์ลัดสำหรับสลับโปรไฟล์ค่าเริ่มต้นคือ **`Ctrl + Alt + L`** หากต้องการเปลี่ยน ให้เปิด **Settings**
คลิกช่อง **Toggle hotkey** แล้วกดปุ่มชุดใหม่ ใช้ **Ctrl**, **Alt** หรือ **Win** ร่วมกับตัวอักษร ตัวเลข หรือ
**F1–F24** (เช่น `Ctrl + Alt + K` หรือ `Win + F9`) ล้างช่องนี้หากต้องการปิดคีย์ลัด
(คลิกที่ไอคอนในถาดระบบยังสลับได้ตามปกติ) ถ้าแอปอื่นใช้ปุ่มชุดนั้นอยู่แล้ว ช่องนี้จะแจ้งให้ทราบทันที

#### ข้อควรรู้

- **ใช้บัญชี Windows เดียวกัน:** รายการภาษาแยกตามบัญชีผู้ใช้ Windows แอปนี้จึงเหมาะกับคนที่ใช้บัญชี
  **เดียวกัน** ถ้าแต่ละคนมีบัญชีของตัวเอง รายการภาษาก็แยกกันอยู่แล้ว
- **ภาษาแรกคือภาษาของหน้าจอ:** ให้ภาษาเมนูของ Windows อยู่บนสุดของทุกโปรไฟล์ (แอปจะเตือนเมื่อไม่ใช่)
- **ชุดภาษา (Language pack):** Windows อาจลบชุดภาษาที่ไม่มีรายการใดใช้งานมาสักระยะ แป้นพิมพ์และ IME
  เป็นส่วนหนึ่งของระบบจึงไม่หาย แต่ส่วนเสริม (เช่น การเขียนด้วยลายมือ เสียงพูด) อาจต้องดาวน์โหลดใหม่
  ป้องกันได้โดยรันคำสั่งนี้ครั้งเดียวใน PowerShell แบบผู้ดูแลระบบ:
  `Disable-ScheduledTask -TaskPath '\Microsoft\Windows\MUI\' -TaskName LPRemove`

### ❤️ สนับสนุนผู้พัฒนา

ดูช่องทาง Buy Me a Coffee, GitHub Sponsors และผู้สนับสนุน GST Topup ได้ที่ [ด้านบน](#support)
แจ้งปัญหาหรือเสนอไอเดียได้ที่ [Issues](https://github.com/Maxkii3/LangProfileSwitcher/issues)

### 📄 สัญญาอนุญาต

© 2026 [Maxkii3](https://github.com/Maxkii3) **สงวนลิขสิทธิ์** ดาวน์โหลดรีลีส หรือรันซอร์สโค้ดโดยไม่แก้ไข
เพื่อใช้งานส่วนตัวได้ การคัดลอก แก้ไข หรือเผยแพร่ซอร์สโค้ดต่อ ต้องได้รับอนุญาตเป็นลายลักษณ์อักษรจากผู้พัฒนา
ดูรายละเอียดใน [LICENSE](LICENSE) (ภาษาอังกฤษ) แอปนี้เป็นเครื่องมืออิสระ ไม่มีส่วนเกี่ยวข้องกับ Microsoft

[⬆ Back to top / กลับด้านบน](#english)
