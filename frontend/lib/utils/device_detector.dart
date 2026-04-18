import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'dart:io';

enum DeviceType { mobile, desktop, web }

class DeviceDetector {
  static const double _mobileWidthBreakpoint = 900;

  static DeviceType detectDevice() {
    if (kIsWeb) {
      return DeviceType.web;
    }
    
    if (Platform.isAndroid || Platform.isIOS) {
      return DeviceType.mobile;
    }
    
    if (Platform.isWindows || Platform.isMacOS || Platform.isLinux) {
      return DeviceType.desktop;
    }
    
    return DeviceType.mobile; // Default fallback
  }

  static bool get isMobile => detectDevice() == DeviceType.mobile;
  static bool get isDesktop => detectDevice() == DeviceType.desktop;
  static bool get isWeb => detectDevice() == DeviceType.web;

  static bool isMobileLayout(BuildContext context) {
    if (!kIsWeb) {
      return isMobile;
    }
    final width = MediaQuery.sizeOf(context).width;
    return width <= _mobileWidthBreakpoint;
  }
}
