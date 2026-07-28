import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(const QuranApp());

class QuranApp extends StatelessWidget {
  const QuranApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFF00695C),
        scaffoldBackgroundColor: const Color(0xFF121212),
        appBarTheme: const AppBarTheme(backgroundColor: Color(0xFF004D40)),
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List surahs = [];
  List filteredSurahs = [];
  bool isLoading = true;

  // Variabel Dynamic Config
  String appTitle = "Al-Qur'an Digital";
  String notificationMessage = "";
  bool showNotification = false;

  // GANTI LINK INI DENGAN URL WEB ADMIN KAMU (Misal dari Render.com)
  final String adminApiUrl = "https://ecological-tariff-compression-idol.trycloudflare.com/api/config";

  @override
  void initState() {
    super.initState();
    fetchAdminConfig();
    fetchSurahs();
  }

  // Mengambil Pengaturan Nama APK & Notifikasi dari Web Admin
  Future<void> fetchAdminConfig() async {
    try {
      final res = await http.get(Uri.parse(adminApiUrl));
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        setState(() {
          appTitle = data['app_name'] ?? "Al-Qur'an Digital";
          notificationMessage = data['notification'] ?? "";
          showNotification = data['show_notification'] ?? false;
        });
      }
    } catch (e) {
      print("Gagal mengambil data admin: $e");
    }
  }

  Future<void> fetchSurahs() async {
    try {
      final res = await http.get(Uri.parse("https://equran.id/api/v2/surat"));
      if (res.statusCode == 200) {
        setState(() {
          surahs = json.decode(res.body)['data'];
          filteredSurahs = surahs;
          isLoading = false;
        });
      }
    } catch (e) {
      print("Gagal mengambil data surah: $e");
    }
  }

  void filterSearch(String query) {
    setState(() {
      filteredSurahs = surahs.where((s) => s['namaLatin'].toLowerCase().contains(query.toLowerCase())).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(appTitle), // Dynamic Header dari Web
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              fetchAdminConfig();
              fetchSurahs();
            },
          )
        ],
      ),
      body: Column(
        children: [
          // Banner Notifikasi Dynamic dari Web Admin
          if (showNotification && notificationMessage.isNotEmpty)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              color: Colors.teal.shade800,
              child: Row(
                children: [
                  const Icon(Icons.notifications_active, color: Colors.amber),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      notificationMessage,
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              onChanged: filterSearch,
              decoration: InputDecoration(
                hintText: "Cari Surah...",
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(30)),
                filled: true,
                fillColor: const Color(0xFF1E1E1E),
              ),
            ),
          ),
          Expanded(
            child: isLoading 
              ? const Center(child: CircularProgressIndicator()) 
              : ListView.builder(
                  itemCount: filteredSurahs.length,
                  itemBuilder: (context, i) {
                    final s = filteredSurahs[i];
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                      color: const Color(0xFF1E1E1E),
                      child: ListTile(
                        leading: CircleAvatar(backgroundColor: Colors.teal, child: Text("${s['nomor']}", style: const TextStyle(color: Colors.white))),
                        title: Text(s['namaLatin'], style: const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Text("${s['arti']} | ${s['jumlahAyat']} Ayat"),
                        trailing: Text(s['nama'], style: const TextStyle(fontSize: 20, color: Colors.tealAccent)),
                        onTap: () => Navigator.push(context, MaterialPageRoute(builder: (c) => DetailSurah(no: s['nomor'], nama: s['namaLatin']))),
                      ),
                    );
                  },
                ),
          ),
        ],
      ),
    );
  }
}

class DetailSurah extends StatelessWidget {
  final int no;
  final String nama;
  const DetailSurah({super.key, required this.no, required this.nama});

  Future<Map> getDetail() async {
    final res = await http.get(Uri.parse("https://equran.id/api/v2/surat/$no"));
    return json.decode(res.body)['data'];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(nama)),
      body: FutureBuilder<Map>(
        future: getDetail(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
          final data = snapshot.data!;
          final ayats = data['ayat'];
          return ListView.builder(
            itemCount: ayats.length,
            itemBuilder: (context, i) {
              final a = ayats[i];
              return Container(
                padding: const EdgeInsets.all(16),
                decoration: const BoxDecoration(border: Border(bottom: BorderSide(color: Colors.white10))),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text("${a['nomorAyat']}", style: const TextStyle(color: Colors.teal)),
                    const SizedBox(height: 10),
                    Text(a['teksArab'], textAlign: TextAlign.right, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, fontFamily: 'serif')),
                    const SizedBox(height: 10),
                    Align(alignment: Alignment.centerLeft, child: Text(a['teksIndonesia'], style: const TextStyle(color: Colors.grey, fontSize: 14))),
                  ],
                ),
              );
            },
          );
        },
      ),
    );
  }
}
