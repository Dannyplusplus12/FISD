import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'config.dart';
import 'theme.dart';
import 'utils/app_mode_manager.dart';
import 'utils/device_detector.dart';
import 'services/notification_service.dart';
import 'services/mobile_notification_service.dart';
import 'services/delivery_proof_sync_service.dart';
import 'screens/home_screen.dart';
import 'screens/mobile_home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppConfig.load();
  await AppModeManager.init();
  await MobileNotificationService.init();
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  static const String _installHintDismissedKey = 'pwa_install_hint_dismissed';

  ThemeMode _themeMode = ThemeMode.light;
  bool _showInstallHint = false;

  void _toggleThemeMode() {
    setState(() {
      _themeMode = _themeMode == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
    });
  }

  @override
  void initState() {
    super.initState();
    // Start polling for pending orders
    NotificationService.startPolling(intervalSeconds: 10);
    NotificationService.onPendingOrdersUpdated = () {
      setState(() {});  // Rebuild to show notification badge
    };

    if (DeviceDetector.isDesktop) {
      DeliveryProofSyncService.startAutoSync(intervalSeconds: 10);
    }

    _loadInstallHintState();
  }

  Future<void> _loadInstallHintState() async {
    final prefs = await SharedPreferences.getInstance();
    final dismissedForever = prefs.getBool(_installHintDismissedKey) ?? false;
    if (!mounted) return;
    setState(() {
      _showInstallHint = !dismissedForever;
    });
  }

  void _dismissInstallHintTemporarily() {
    if (!mounted) return;
    setState(() => _showInstallHint = false);
  }

  Future<void> _dismissInstallHintForever() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_installHintDismissedKey, true);
    if (!mounted) return;
    setState(() => _showInstallHint = false);
  }

  @override
  void dispose() {
    NotificationService.stopPolling();
    DeliveryProofSyncService.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Fisd',
      debugShowCheckedModeBanner: false,
      theme: buildLightTheme(),
      darkTheme: buildDarkTheme(),
      themeMode: _themeMode,
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('vi', 'VN'),
        Locale('en', 'US'),
      ],
      locale: const Locale('vi', 'VN'),
      home: Builder(
        builder: (context) {
          final useMobileLayout = DeviceDetector.isMobileLayout(context);
          final showInstallHint = kIsWeb && useMobileLayout && _showInstallHint;
          final home = useMobileLayout
              ? const MobileHomeScreen()
              : HomeScreen(
                  isDarkMode: _themeMode == ThemeMode.dark,
                  onToggleTheme: _toggleThemeMode,
                );

          if (!showInstallHint) {
            return home;
          }

          return Stack(
            children: [
              home,
              SafeArea(
                child: Align(
                  alignment: Alignment.topCenter,
                  child: Container(
                    margin: const EdgeInsets.fromLTRB(12, 8, 12, 0),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFE5E7EB)),
                      boxShadow: const [
                        BoxShadow(
                          color: Color(0x22000000),
                          blurRadius: 10,
                          offset: Offset(0, 3),
                        )
                      ],
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Cài Fisd lên Màn hình chính',
                          style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Safari: Nhấn Chia sẻ (□↑) → Thêm vào Màn hình chính.',
                          style: TextStyle(fontSize: 12, color: Color(0xFF475569)),
                        ),
                        const SizedBox(height: 10),
                        Row(
                          children: [
                            TextButton(
                              onPressed: _dismissInstallHintTemporarily,
                              child: const Text('Đã hiểu'),
                            ),
                            const SizedBox(width: 8),
                            OutlinedButton(
                              onPressed: _dismissInstallHintForever,
                              child: const Text('Không nhắc lại'),
                            ),
                          ],
                        )
                      ],
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
