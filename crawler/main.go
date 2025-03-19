package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"strconv"
	"strings"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// Estrutura para armazenar o resultado da Lotofácil
type ResultadoLotofacil struct {
	Concurso int      `json:"numero"`
	Data     string   `json:"dataApuracao"`
	Numeros  []string `json:"dezenasSorteadasOrdemSorteio"`
}

// Função para conectar ao MongoDB
func connectMongoDB() (*mongo.Client, error) {
	clientOptions := options.Client().ApplyURI("mongodb://localhost:27017")
	client, err := mongo.Connect(context.TODO(), clientOptions)
	if err != nil {
		return nil, err
	}
	return client, nil
}

// Função para buscar o resultado mais recente da Lotofácil
func fetchLatestResult(consurso int) (*ResultadoLotofacil, error) {
	url := "https://api.guidi.dev.br/loteria/lotofacil/"

	resp, err := http.Get(strings.Join([]string{url, strconv.Itoa(consurso)}, ""))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	b, err := httputil.DumpResponse(resp, true)
	if err != nil {
		log.Fatalln(err)
	}

	fmt.Println(string(b))

	var resultado ResultadoLotofacil
	err = json.NewDecoder(resp.Body).Decode(&resultado)
	if err != nil {
		return nil, err
	}
	return &resultado, nil
}

// Função para salvar o resultado no MongoDB
func saveResult(collection *mongo.Collection, resultado *ResultadoLotofacil) error {
	// Verifica se o concurso já existe no banco de dados
	filter := bson.M{"concurso": resultado.Concurso}
	count, err := collection.CountDocuments(context.TODO(), filter)
	if err != nil {
		return err
	}
	if count > 0 {
		fmt.Println("Concurso já existe no banco de dados:", resultado.Concurso)
		return nil
	}

	// Insere o novo resultado
	_, err = collection.InsertOne(context.TODO(), resultado)
	if err != nil {
		return err
	}
	fmt.Println("Resultado salvo com sucesso:", resultado)
	return nil
}

func main() {
	// Conecta ao MongoDB
	client, err := connectMongoDB()
	if err != nil {
		log.Fatal("Erro ao conectar ao MongoDB:", err)
	}
	defer client.Disconnect(context.TODO())

	// Seleciona o banco de dados e a coleção
	db := client.Database("lotofacil")
	collection := db.Collection("resultados")

	// Busca o resultado mais recente da Lotofácil
	for i := 3341; i < 3346; i++ {
		resultado, err := fetchLatestResult(i)
		if err != nil {
			log.Fatal("Erro ao buscar o resultado mais recente:", err)
		}

		// Salva o resultado no MongoDB
		err = saveResult(collection, resultado)
		if err != nil {
			log.Fatal("Erro ao salvar o resultado no MongoDB:", err)
		}
	}

}
