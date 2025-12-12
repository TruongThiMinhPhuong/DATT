import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class SupabaseService extends ChangeNotifier {
  final SupabaseClient _supabase = Supabase.instance.client;

  bool _isInitialized = false;
  Map<String, dynamic> _statistics = {};
  List<Map<String, dynamic>> _recentClassifications = [];
  RealtimeChannel? _channel;

  bool get isInitialized => _isInitialized;
  Map<String, dynamic> get statistics => _statistics;
  List<Map<String, dynamic>> get recentClassifications => _recentClassifications;
  User? get currentUser => _supabase.auth.currentUser;

  SupabaseService() {
    _initialize();
  }

  Future<void> _initialize() async {
    // Listen to auth state changes
    _supabase.auth.onAuthStateChange.listen((data) {
      notifyListeners();
    });

    // Listen to classifications updates
    _listenToClassifications();

    _isInitialized = true;
    notifyListeners();
  }

  void _listenToClassifications() {
    _channel = _supabase.channel('classifications-channel')
      .onPostgresChanges(
        event: PostgresChangeEvent.all,
        schema: 'public',
        table: 'classifications',
        callback: (payload) {
          // Refresh data when changes occur
          refreshData();
        },
      )
      .subscribe();

    // Initial data load
    refreshData();
  }

  void _updateStatistics() {
    final stats = <String, int>{
      'fresh_fruit': 0,
      'spoiled_fruit': 0,
      'other': 0,
      'total': 0,
    };

    for (final item in _recentClassifications) {
      final classification = item['classification'] as String?;
      if (classification != null && stats.containsKey(classification)) {
        stats[classification] = (stats[classification] ?? 0) + 1;
      }
      stats['total'] = (stats['total'] ?? 0) + 1;
    }

    _statistics = stats;
  }

  Future<void> refreshData() async {
    try {
      final response = await _supabase
          .from('classifications')
          .select()
          .order('timestamp', ascending: false)
          .limit(20);

      _recentClassifications = List<Map<String, dynamic>>.from(response);

      _updateStatistics();
      notifyListeners();
    } catch (e) {
      debugPrint('Error fetching classifications: $e');
    }
  }

  Future<void> signInWithGoogle() async {
    try {
      await _supabase.auth.signInWithOAuth(
        OAuthProvider.google,
        redirectTo: 'io.supabase.fruitclassification://callback',
      );
      notifyListeners();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> signInWithEmail(String email, String password) async {
    try {
      await _supabase.auth.signInWithPassword(
        email: email,
        password: password,
      );
      notifyListeners();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> signUp(String email, String password) async {
    try {
      await _supabase.auth.signUp(
        email: email,
        password: password,
      );
      notifyListeners();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> signOut() async {
    await _supabase.auth.signOut();
    notifyListeners();
  }

  Future<String?> getUserRole() async {
    final user = currentUser;
    if (user == null) return null;

    try {
      final response = await _supabase
          .from('users')
          .select('role')
          .eq('id', user.id)
          .single();

      return response['role'] as String?;
    } catch (e) {
      return 'viewer';
    }
  }

  String getImageUrl(String path) {
    return _supabase.storage.from('fruit-images').getPublicUrl(path);
  }

  @override
  void dispose() {
    _channel?.unsubscribe();
    super.dispose();
  }
}
