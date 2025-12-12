import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';

class FirebaseService extends ChangeNotifier {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;

  bool _isInitialized = false;
  Map<String, dynamic> _statistics = {};
  List<Map<String, dynamic>> _recentClassifications = [];

  bool get isInitialized => _isInitialized;
  Map<String, dynamic> get statistics => _statistics;
  List<Map<String, dynamic>> get recentClassifications => _recentClassifications;
  User? get currentUser => _auth.currentUser;

  FirebaseService() {
    _initialize();
  }

  Future<void> _initialize() async {
    // Listen to auth state changes
    _auth.authStateChanges().listen((User? user) {
      notifyListeners();
    });

    // Listen to statistics updates
    _listenToClassifications();

    _isInitialized = true;
    notifyListeners();
  }

  void _listenToClassifications() {
    _firestore
        .collection('classifications')
        .orderBy('timestamp', descending: true)
        .limit(20)
        .snapshots()
        .listen((snapshot) {
      _recentClassifications = snapshot.docs
          .map((doc) => {...doc.data(), 'id': doc.id})
          .toList();

      _updateStatistics();
      notifyListeners();
    });
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
    // Force refresh by re-fetching data
    final snapshot = await _firestore
        .collection('classifications')
        .orderBy('timestamp', descending: true)
        .limit(20)
        .get();

    _recentClassifications = snapshot.docs
        .map((doc) => {...doc.data(), 'id': doc.id})
        .toList();

    _updateStatistics();
    notifyListeners();
  }

  Future<void> signInWithGoogle() async {
    try {
      // TODO: Implement Google Sign In
      // This requires google_sign_in package
      notifyListeners();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> signOut() async {
    await _auth.signOut();
    notifyListeners();
  }
}
