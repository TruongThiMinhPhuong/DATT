import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/supabase_service.dart';
import '../widgets/stat_card.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🍎 Fruit Classification'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              context.read<SupabaseService>().refreshData();
            },
          ),
        ],
      ),
      body: Consumer<SupabaseService>(
        builder: (context, supabase, child) {
          if (!supabase.isInitialized) {
            return const Center(child: CircularProgressIndicator());
          }

          final stats = supabase.statistics;

          return RefreshIndicator(
            onRefresh: () => supabase.refreshData(),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Statistics Cards
                  GridView.count(
                    crossAxisCount: 2,
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    children: [
                      StatCard(
                        title: 'Fresh Fruit',
                        value: stats['fresh_fruit']?.toString() ?? '0',
                        icon: Icons.check_circle,
                        color: Colors.green,
                      ),
                      StatCard(
                        title: 'Spoiled',
                        value: stats['spoiled_fruit']?.toString() ?? '0',
                        icon: Icons.warning,
                        color: Colors.red,
                      ),
                      StatCard(
                        title: 'Other',
                        value: stats['other']?.toString() ?? '0',
                        icon: Icons.help_outline,
                        color: Colors.orange,
                      ),
                      StatCard(
                        title: 'Total',
                        value: stats['total']?.toString() ?? '0',
                        icon: Icons.bar_chart,
                        color: Colors.blue,
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Recent Classifications
                  const Text(
                    'Recent Classifications',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  
                  ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: supabase.recentClassifications.length,
                    itemBuilder: (context, index) {
                      final item = supabase.recentClassifications[index];
                      return Card(
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: _getColor(item['classification']),
                            child: Text(_getEmoji(item['classification'])),
                          ),
                          title: Text(item['classification'] ?? 'Unknown'),
                          subtitle: Text(
                            'Confidence: ${(item['confidence'] * 100).toStringAsFixed(1)}%',
                          ),
                          trailing: Text(
                            _formatTime(item['timestamp']),
                            style: const TextStyle(fontSize: 12),
                          ),
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Color _getColor(String? classification) {
    switch (classification) {
      case 'fresh_fruit':
        return Colors.green;
      case 'spoiled_fruit':
        return Colors.red;
      default:
        return Colors.orange;
    }
  }

  String _getEmoji(String? classification) {
    switch (classification) {
      case 'fresh_fruit':
        return '🍏';
      case 'spoiled_fruit':
        return '🍎';
      default:
        return '📦';
    }
  }

  String _formatTime(dynamic timestamp) {
    if (timestamp == null) return '';
    // Simple time formatting - you can use intl package for better formatting
    final date = DateTime.fromMillisecondsSinceEpoch((timestamp * 1000).toInt());
    return '${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }
}
