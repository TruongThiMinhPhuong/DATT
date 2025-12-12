import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

// Supabase Configuration
const supabaseConfig = {
    url: 'https://your-project.supabase.co',
    anonKey: 'your-anon-key'
};

// Initialize Supabase
const supabase = createClient(supabaseConfig.url, supabaseConfig.anonKey);

// Export for use in app.js
window.supabase = supabase;

// Auth helper functions
window.supabaseAuth = {
    signInWithGoogle: async () => {
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: window.location.origin
            }
        });
        if (error) throw error;
        return data;
    },
    
    signInWithEmail: async (email, password) => {
        const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password
        });
        if (error) throw error;
        return data;
    },
    
    signUp: async (email, password) => {
        const { data, error } = await supabase.auth.signUp({
            email,
            password
        });
        if (error) throw error;
        return data;
    },
    
    signOut: async () => {
        const { error } = await supabase.auth.signOut();
        if (error) throw error;
    },
    
    getSession: async () => {
        const { data: { session } } = await supabase.auth.getSession();
        return session;
    },
    
    onAuthStateChange: (callback) => {
        return supabase.auth.onAuthStateChange((event, session) => {
            callback(session?.user || null);
        });
    }
};

// Database helper functions
window.supabaseDb = {
    // Get recent classifications
    getRecentClassifications: async (limit = 20) => {
        const { data, error } = await supabase
            .from('classifications')
            .select('*')
            .order('timestamp', { ascending: false })
            .limit(limit);
        
        if (error) throw error;
        return data;
    },
    
    // Subscribe to realtime changes
    subscribeToClassifications: (callback) => {
        return supabase
            .channel('classifications-changes')
            .on('postgres_changes', 
                { event: '*', schema: 'public', table: 'classifications' },
                (payload) => callback(payload)
            )
            .subscribe();
    },
    
    // Get user role
    getUserRole: async (userId) => {
        const { data, error } = await supabase
            .from('users')
            .select('role')
            .eq('id', userId)
            .single();
        
        if (error) return 'viewer';
        return data?.role || 'viewer';
    },
    
    // Get statistics
    getStatistics: async () => {
        const { data, error } = await supabase
            .from('classifications')
            .select('classification, confidence');
        
        if (error) throw error;
        
        const stats = {
            total: data.length,
            fresh_fruit: 0,
            spoiled_fruit: 0,
            other: 0,
            avg_confidence: 0
        };
        
        let totalConfidence = 0;
        for (const item of data) {
            if (item.classification === 'fresh_fruit') stats.fresh_fruit++;
            else if (item.classification === 'spoiled_fruit') stats.spoiled_fruit++;
            else stats.other++;
            totalConfidence += item.confidence || 0;
        }
        
        stats.avg_confidence = stats.total > 0 ? totalConfidence / stats.total : 0;
        return stats;
    }
};

// Storage helper functions
window.supabaseStorage = {
    getPublicUrl: (path) => {
        const { data } = supabase.storage.from('fruit-images').getPublicUrl(path);
        return data.publicUrl;
    },
    
    uploadImage: async (file, path) => {
        const { data, error } = await supabase.storage
            .from('fruit-images')
            .upload(path, file, {
                contentType: 'image/jpeg'
            });
        
        if (error) throw error;
        return data;
    }
};

console.log('Supabase initialized');
