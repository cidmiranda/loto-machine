import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Previsão de Números',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: PredictionScreen(),
    );
  }
}

class PredictionScreen extends StatefulWidget {
  const PredictionScreen({super.key});

  @override
  _PredictionScreenState createState() => _PredictionScreenState();
}

class _PredictionScreenState extends State<PredictionScreen> {
  String prediction = '';
  final TextEditingController _controller = TextEditingController();

  // Variável para armazenar a URL base do servidor
  final String baseUrl =
      'http://localhost:8080/predict'; // Altere conforme necessário

  // Função para fazer a requisição POST ao backend
  Future<void> getPrediction(String numbers) async {
    try {
      // Converte os números inseridos em uma lista de inteiros
      List<int> numberList =
          numbers.split(',').map((e) => int.tryParse(e.trim()) ?? 0).toList();

      // Monta o JSON com os números
      var body = jsonEncode({'numbers': numberList});

      // Faz a requisição POST
      final response = await http.post(
        Uri.parse('http://localhost:8080/predict'), // URL do seu backend
        headers: {'Content-Type': 'application/json'},
        body: body,
      );

      // Verificar o conteúdo da resposta
      print('Resposta: ${response.body}');

      if (response.statusCode == 200) {
        var jsonResponse = jsonDecode(response.body);

        // Certifique-se de que a chave 'prediction' existe e é uma lista
        if (jsonResponse.containsKey('prediction')) {
          var predictionList = jsonResponse['prediction'];

          // Verifica se a previsão está no formato esperado (lista de strings)
          if (predictionList is List) {
            setState(() {
              // Junta os números da previsão em uma string, separados por vírgula
              prediction = predictionList.join(', ');
            });
          } else {
            setState(() {
              prediction = 'Formato inesperado de previsão.';
            });
          }
        } else {
          setState(() {
            prediction = 'Erro: chave "prediction" não encontrada.';
          });
        }
      } else {
        setState(() {
          prediction =
              'Erro ao obter a previsão. Status Code: ${response.statusCode}';
        });
      }
    } catch (e) {
      print('Erro: $e');
      setState(() {
        prediction = 'Erro ao conectar ao servidor.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Previsão de Números')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: <Widget>[
            TextField(
              controller: _controller,
              decoration: InputDecoration(
                labelText:
                    'Digite os números (ex: 11, 14, 16, 5, 23, 8, 20, 25, 7, 3, 15, 1, 21, 9, 12)',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                prediction = "";
                String input = _controller.text;
                if (input.isNotEmpty) {
                  getPrediction(input); // Chama a função para fazer a previsão
                }
              },
              child: Text('Prever Números'),
            ),
            SizedBox(height: 20),
            prediction.isNotEmpty
                ? Text('Previsão: $prediction')
                : Container(), // Exibe a previsão quando ela está disponível
          ],
        ),
      ),
    );
  }
}
