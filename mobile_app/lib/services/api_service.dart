import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService extends ChangeNotifier {
  final String baseUrl;

  ApiService({this.baseUrl = 'http://100.112.253.55:8000'});

  Future<Map<String, dynamic>> getStatistics() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/stats'));
      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      throw Exception('Failed to load statistics');
    } catch (e) {
      rethrow;
    }
  }

  Future<List<dynamic>> getHistory({int limit = 100}) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/history?limit=$limit'),
      );
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['history'] as List<dynamic>;
      }
      throw Exception('Failed to load history');
    } catch (e) {
      rethrow;
    }
  }

  // Hardware control methods (Admin only)
  Future<void> startConveyor({String? authToken}) async {
    await _sendHardwareCommand('conveyor/start', authToken: authToken);
  }

  Future<void> stopConveyor({String? authToken}) async {
    await _sendHardwareCommand('conveyor/stop', authToken: authToken);
  }

  Future<void> setConveyorSpeed(int speed, {String? authToken}) async {
    await _sendHardwareCommand(
      'conveyor/speed',
      body: {'speed': speed},
      authToken: authToken,
    );
  }

  Future<void> moveServo(String position, {String? authToken}) async {
    await _sendHardwareCommand(
      'servo/move',
      body: {'position': position},
      authToken: authToken,
    );
  }

  Future<void> captureImage({String? authToken}) async {
    await _sendHardwareCommand('camera/capture', authToken: authToken);
  }

  Future<void> emergencyStop({String? authToken}) async {
    await _sendHardwareCommand('emergency-stop', authToken: authToken);
  }

  Future<void> _sendHardwareCommand(
    String endpoint, {
    Map<String, dynamic>? body,
    String? authToken,
  }) async {
    try {
      final headers = <String, String>{
        'Content-Type': 'application/json',
        if (authToken != null) 'Authorization': 'Bearer $authToken',
      };

      final response = await http.post(
        Uri.parse('$baseUrl/api/hardware/$endpoint'),
        headers: headers,
        body: body != null ? json.encode(body) : null,
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to execute command: ${response.body}');
      }
    } catch (e) {
      rethrow;
    }
  }
}
