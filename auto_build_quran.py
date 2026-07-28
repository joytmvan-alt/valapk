import os
import subprocess

print("=== QURAN DIGITAL AUTO BUILDER ===")
github_user = input("Username GitHub: ").strip()
github_repo = input("Nama Repo (misal: quran-digital): ").strip()
github_token = input("Personal Access Token (PAT): ").strip()

repo_url = f"https://{github_user}:{github_token}@github.com/{github_user}/{github_repo}.git"

# 1. KODE FLUTTER (UI MODERN + API INTEGRATION)
flutter_dart = """
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

  @override
  void initState() {
    super.initState();
    fetchSurahs();
  }

  Future<void> fetchSurahs() async {
    final res = await http.get(Uri.parse("https://equran.id/api/v2/surat"));
    if (res.statusCode == 200) {
      setState(() {
        surahs = json.decode(res.body)['data'];
        filteredSurahs = surahs;
        isLoading = false;
      });
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
      appBar: AppBar(title: const Text("Al-Qur'an Digital")),
      body: Column(
        children: [
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
"""

# 2. CONFIG FILES & WORKFLOW (SAMA SEPERTI SEBELUMNYA)
pubspec = """name: quran_digital
dependencies:
  flutter: { sdk: flutter }
  http: ^1.1.0
flutter: { uses-material-design: true }
"""

workflow = """name: Build APK
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-java@v4
      with: { java-version: '17', distribution: 'zulu' }
    - uses: subosito/flutter-action@v2
      with: { flutter-version: '3.x' }
    - run: flutter create . --platforms=android --org com.quran.digital
    - run: flutter pub get
    - run: flutter build apk --release
    - uses: actions/upload-artifact@v4
      with: { name: Quran-APK, path: build/app/outputs/flutter-apk/app-release.apk }
"""

# EKSEKUSI PUSH KE GITHUB
os.makedirs("quran_project/lib", exist_ok=True)
os.makedirs("quran_project/.github/workflows", exist_ok=True)
with open("quran_project/lib/main.dart", "w") as f: f.write(flutter_dart)
with open("quran_project/pubspec.yaml", "w") as f: f.write(pubspec)
with open("quran_project/.github/workflows/build.yml", "w") as f: f.write(workflow)

os.chdir("quran_project")
subprocess.run(["git", "init"])
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "Build Quran App"])
subprocess.run(["git", "branch", "-M", "main"])
subprocess.run(["git", "remote", "add", "origin", repo_url])
subprocess.run(["git", "push", "-u", "origin", "main", "--force"])

print(f"🚀 BERHASIL! Cek Actions di: https://github.com/{github_user}/{github_repo}/actions")

