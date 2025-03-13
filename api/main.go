package main

import (
	"bytes"
	"fmt"
	"net/http"
	"os/exec"
	"strconv"
	"strings"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// Estrutura do sorteio
type Sorteio struct {
	Concurso int      `json:"concurso" bson:"concurso"`
	Data     string   `json:"data" bson:"data"`
	Numeros  []string `json:"numeros" bson:"numeros"`
}

type InputData struct {
	Numbers []int `json:"numbers"`
}

// Conectar ao MongoDB
func connectMongoDB(c *gin.Context) (*mongo.Client, error) {
	clientOptions := options.Client().ApplyURI("mongodb://localhost:27017")
	client, err := mongo.Connect(c, clientOptions)
	if err != nil {
		return nil, err
	}
	return client, nil
}

// Função para listar os últimos sorteios
func getUltimosSorteios(c *gin.Context) {
	client, err := connectMongoDB(c)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Erro ao conectar ao MongoDB"})
		return
	}
	defer client.Disconnect(c)

	collection := client.Database("lotofacil").Collection("resultados")

	// Busca os últimos 10 sorteios
	cursor, err := collection.Find(c, bson.D{}, options.Find().SetSort(bson.D{{Key: "concurso", Value: -1}}).SetLimit(10))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Erro ao buscar os sorteios"})
		return
	}
	defer cursor.Close(c)

	var sorteios []Sorteio
	for cursor.Next(c) {
		var sorteio Sorteio
		err := cursor.Decode(&sorteio)
		if err == nil {
			sorteios = append(sorteios, sorteio)
		}
	}

	c.JSON(http.StatusOK, sorteios)
}

// Função para buscar um sorteio pelo número do concurso
func getSorteioPorConcurso(c *gin.Context) {
	client, err := connectMongoDB(c)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Erro ao conectar ao MongoDB"})
		return
	}
	defer client.Disconnect(c)

	concurso, err := strconv.Atoi(c.Param("concurso"))
	if err != nil {
		return
	}
	collection := client.Database("lotofacil").Collection("resultados")

	var sorteio Sorteio
	filter := bson.M{"concurso": concurso}
	err = collection.FindOne(c, filter).Decode(&sorteio)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Concurso não encontrado"})
		return
	}

	c.JSON(http.StatusOK, sorteio)
}

func predictHandler(c *gin.Context) {
	var input InputData
	// Decodifica os dados de entrada
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	// Chama o script Python para fazer a previsão
	cmd := exec.Command("python", "../ai/predict.py", strings.Trim(strings.Join(strings.Fields(fmt.Sprint(input.Numbers)), ","), "[]"))
	fmt.Println(strings.Trim(strings.Join(strings.Fields(fmt.Sprint(input.Numbers)), ","), "[]"))
	// Capturar a saída padrão e de erro
	var out bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &stderr

	// Executa o comando
	err := cmd.Run()
	if err != nil {
		fmt.Println("Erro ao executar o script Python:", err)
		fmt.Println("Saída de erro:", stderr.String()) // Mostra o erro do Python
		return
	}

	prediction := strings.TrimSpace(out.String())      // Remover espaços extras
	predictedNumbers := strings.Split(prediction, ",") // Separar por vírgula
	// Exibir saída do script
	fmt.Println("Saída do script Python:", out.String())
	/*
			output, err := cmd.Output()
			if err != nil {
				log.Printf("Erro ao executar o script Python: %v", err)
				c.JSON(500, gin.H{"error": "Erro ao executar o script Python"})
				return
			}

		// Envia a resposta com a previsão
		var prediction float64
		_, err = fmt.Sscanf(string(output), "%f", &prediction)
		if err != nil {
			log.Printf("Erro ao processar a previsão: %v", err)
			c.JSON(500, gin.H{"error": "Erro ao processar a previsão"})
			return
		}
	*/
	c.JSON(200, gin.H{
		"prediction": predictedNumbers,
	})

}
func main() {
	r := gin.Default()
	// Configura o middleware CORS
	r.Use(cors.Default())

	// Rotas da API
	r.GET("/sorteios", getUltimosSorteios)             // Lista os últimos sorteios
	r.GET("/sorteio/:concurso", getSorteioPorConcurso) // Busca um concurso específico
	r.POST("/predict", predictHandler)
	// Inicia o servidor na porta 8080
	r.Run(":8080")
}
