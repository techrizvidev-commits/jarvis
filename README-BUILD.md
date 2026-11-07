# Build APK + EXE — after you connect Git

## 1. Git connect karo (tum kar rahe ho)
1. GitHub pe naya repo banao, naam: `jarvis`
2. Is `jarvis` folder ko push karo:
   ```
   git init
   git add .
   git commit -m "Jarvis v3 - HUD + mobile"
   git branch -M main
   git remote add origin https://github.com/<tumhara-username>/jarvis.git
   git push -u origin main
   ```
3. Push hote hi GitHub Actions automatically chalega.

## 2. APK + EXE kahan milega
GitHub repo → **Actions** tab → latest run → **Artifacts**:
- `Jarvis-Windows-exe` — `Jarvis.exe` (Windows, HUD server + controls)
- `Jarvis-Android-apk` — `app-debug.apk` (Android phone, install karo)

Ye debug APK hai — Play Store ke liye nahi, direct install ke liye hai. Phone pe "Install unknown apps" allow karna padega.

## 3. Local build (agar GitHub na chaho)
Windows EXE:
```
build_exe.bat
```
APK local: Android Studio + `mobile-app/` me `npm ci && npx cap sync android` — pehli baar thoda setup mangta hai, is liye GitHub Actions easy raasta hai.

## 4. APK kaam kaise karega
APK me mobile UI hai. Phone aur laptop **same Wi-Fi** pe hon, aur laptop pe `Jarvis.exe` / `start_jarvis.bat` chal raha ho. Phone app me server address laptop ka IP hota hai — pehli baar mobile.html kholo to wo auto-detect karta hai jab same server se serve ho.
Ghar se bahar se control chahiye to Tailscale/ngrok lagana padega — wo agla step hai.
