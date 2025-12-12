import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/supabase_service.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<SupabaseService>(
      builder: (context, supabase, child) {
        final user = supabase.currentUser;

        return Scaffold(
          appBar: AppBar(
            title: const Text('Settings'),
          ),
          body: ListView(
            children: [
              // User Info
              if (user != null)
                UserAccountsDrawerHeader(
                  accountName: Text(user.userMetadata?['name'] ?? 'User'),
                  accountEmail: Text(user.email ?? ''),
                  currentAccountPicture: CircleAvatar(
                    backgroundImage: user.userMetadata?['avatar_url'] != null
                        ? NetworkImage(user.userMetadata!['avatar_url'])
                        : null,
                    child: user.userMetadata?['avatar_url'] == null
                        ? const Icon(Icons.person, size: 40)
                        : null,
                  ),
                ),

              // Account Section
              _buildSectionHeader('Account'),
              if (user == null)
                ListTile(
                  leading: const Icon(Icons.login),
                  title: const Text('Sign In'),
                  subtitle: const Text('Sign in to sync data'),
                  onTap: () {
                    _showSignInDialog(context, supabase);
                  },
                )
              else
                ListTile(
                  leading: const Icon(Icons.logout),
                  title: const Text('Sign Out'),
                  onTap: () async {
                    await supabase.signOut();
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Signed out successfully')),
                      );
                    }
                  },
                ),

              const Divider(),

              // Notifications Section
              _buildSectionHeader('Notifications'),
              SwitchListTile(
                secondary: const Icon(Icons.notifications),
                title: const Text('Push Notifications'),
                subtitle: const Text('Get notified of new classifications'),
                value: true, // TODO: Connect to actual setting
                onChanged: (value) {
                  // TODO: Implement notification toggle
                },
              ),

              const Divider(),

              // App Info Section
              _buildSectionHeader('About'),
              ListTile(
                leading: const Icon(Icons.info),
                title: const Text('Version'),
                subtitle: const Text('1.0.0'),
              ),
              ListTile(
                leading: const Icon(Icons.description),
                title: const Text('Open Source Licenses'),
                onTap: () {
                  showLicensePage(
                    context: context,
                    applicationName: 'Fruit Classification',
                    applicationVersion: '1.0.0',
                  );
                },
              ),

              const Divider(),

              // Theme Section
              _buildSectionHeader('Appearance'),
              ListTile(
                leading: const Icon(Icons.palette),
                title: const Text('Theme'),
                subtitle: const Text('System default'),
                onTap: () {
                  // TODO: Implement theme selection
                },
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.grey[600],
        ),
      ),
    );
  }

  void _showSignInDialog(BuildContext context, SupabaseService supabase) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Sign In'),
        content: const Text(
          'Sign in with your account to sync data across devices and access all features.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              try {
                await supabase.signInWithGoogle();
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Sign in failed: $e')),
                  );
                }
              }
            },
            child: const Text('Sign In with Google'),
          ),
        ],
      ),
    );
  }
}
