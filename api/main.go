package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"sort"
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
	Par      int      `json:"par" bson:"par"`
	Impar    int      `json:"impar" bson:"impar"`
}

type InputData struct {
	Numbers  []int `json:"numbers"`
	Concurso []int `json:"concurso"`
}

type NumeroFrequencia struct {
	Numero     int `bson:"_id"`
	Frequencia int `bson:"frequencia"`
}

type NumeroFrequencias struct {
	MaisSorteados  []NumeroFrequencia `bson:"maisSorteados"`
	MenosSorteados []NumeroFrequencia `bson:"menosSorteados"`
	Sorteados      []NumeroFrequencia `bson:"sorteados"`
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
			par, impar := countParImpar(sorteio.Numeros)
			sorteio.Par = par
			sorteio.Impar = impar
			sorteios = append(sorteios, sorteio)
		}
	}

	c.JSON(http.StatusOK, sorteios)
}

// mais saíram (1 a 10)
// menos saíram (11 a 15)
// menos saíram (26 a 16)
// mais saíram (1 a 5)
// ranking
func countParImpar(numeros []string) (int, int) {
	par := 0
	impar := 0
	for i := 0; i < len(numeros); i++ {
		numero := numeros[i]
		i, _ := strconv.Atoi(numero)
		if i%2 == 0 {
			par += 1
		} else {
			impar += 1
		}

	}
	return par, impar
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
	par, impar := countParImpar(sorteio.Numeros)
	sorteio.Par = par
	sorteio.Impar = impar
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Concurso não encontrado"})
		return
	}

	c.JSON(http.StatusOK, sorteio)
}

// Função para calcular a frequência dos números
func calcularFrequencia(c *gin.Context, collection *mongo.Collection, ordem int, limite int) ([]NumeroFrequencia, error) {
	// Pipeline de agregação no MongoDB
	pipeline := mongo.Pipeline{
		{{Key: "$unwind", Value: "$numeros"}}, // Expande o array de números
		{{Key: "$group", Value: bson.D{
			{Key: "_id", Value: "$numeros"},
			{Key: "frequencia", Value: bson.D{{Key: "$sum", Value: 1}}},
		}}},
		{{Key: "$sort", Value: bson.D{{Key: "frequencia", Value: ordem}}}}, // Ordenação (ascendente ou descendente)
		{{Key: "$limit", Value: limite}},                                   // Pegar os top 5 mais ou menos sorteados
	}

	// Executar a agregação
	cursor, err := collection.Aggregate(c, pipeline)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(c)

	// Ler os resultados brutos
	var rawResults []bson.M
	if err = cursor.All(c, &rawResults); err != nil {
		return nil, err
	}

	// Converter os resultados corretamente
	var resultados []NumeroFrequencia
	for _, item := range rawResults {
		var numeroInt int

		// Tenta converter `_id` para int
		switch v := item["_id"].(type) {
		case int32:
			numeroInt = int(v)
		case int64:
			numeroInt = int(v)
		case string:
			numeroInt, _ = strconv.Atoi(v) // Converte string para int
		default:
			return nil, fmt.Errorf("tipo inesperado de número: %v", item["_id"])
		}

		// Adiciona ao slice final
		resultados = append(resultados, NumeroFrequencia{
			Numero:     numeroInt,
			Frequencia: int(item["frequencia"].(int32)), // Frequência sempre é número
		})
	}

	return resultados, nil
}

// Função para buscar os núemros que mais saem
func getNumerosMaisMenosSorteados(c *gin.Context) {
	client, err := connectMongoDB(c)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Erro ao conectar ao MongoDB"})
		return
	}
	defer client.Disconnect(c)

	collection := client.Database("lotofacil").Collection("resultados")

	// Exibir resultados
	var retorno NumeroFrequencias
	numerosMaisSorteados, err := calcularFrequencia(c, collection, -1, 5) // Mais sorteados
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}
	retorno.MaisSorteados = numerosMaisSorteados

	numerosMenosSorteados, err := calcularFrequencia(c, collection, 1, 5) // Menos sorteados
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}
	retorno.MenosSorteados = numerosMenosSorteados

	sorteados, err := calcularFrequencia(c, collection, -1, 25) // Todos
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}
	retorno.Sorteados = sorteados

	c.JSON(http.StatusOK, retorno)
}

func frequenciasHandler(c *gin.Context) {

	// Chama o script Python para fazer a previsão
	cmd := exec.Command("C:\\Users\\Cid\\anaconda3\\python.exe", "../ai/lotofacil/frequencias.py")

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

	// Variável para armazenar o JSON convertido
	var frequencias map[string]int

	// Exibir saída do script
	fmt.Println("Saída do script Python:", out.String())

	err = json.Unmarshal(out.Bytes(), &frequencias)
	if err != nil {
		fmt.Println("Erro ao converter JSON: %v", err)
		c.JSON(500, gin.H{"error": "Erro ao converter JSON"})
		return
	}

	c.JSON(200, gin.H{
		"frequencias": frequencias,
	})
}

func parImparHandler(c *gin.Context) {

	// Chama o script Python para fazer a previsão
	cmd := exec.Command("C:\\Users\\Cid\\anaconda3\\python.exe", "../ai/lotofacil/par_impar.py")

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

	// Variável para armazenar o JSON convertido
	var parImpar map[string]int

	// Exibir saída do script
	fmt.Println("Saída do script Python:", out.String())

	err = json.Unmarshal(out.Bytes(), &parImpar)
	if err != nil {
		fmt.Println("Erro ao converter JSON: %v", err)
		c.JSON(500, gin.H{"error": "Erro ao converter JSON"})
		return
	}

	c.JSON(200, gin.H{
		"parImpar": parImpar,
	})
}

func faixasHandler(c *gin.Context) {

	// Chama o script Python para fazer a previsão
	cmd := exec.Command("C:\\Users\\Cid\\anaconda3\\python.exe", "../ai/lotofacil/faixas.py")

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

	// Variável para armazenar o JSON convertido
	var faixas map[string]int

	// Exibir saída do script
	fmt.Println("Saída do script Python:", out.String())

	err = json.Unmarshal(out.Bytes(), &faixas)
	if err != nil {
		fmt.Println("Erro ao converter JSON: %v", err)
		c.JSON(500, gin.H{"error": "Erro ao converter JSON"})
		return
	}

	c.JSON(200, gin.H{
		"faixas": faixas,
	})
}
func somaHandler(c *gin.Context) {

	type SomaHistorica struct {
		Concurso    int `json:"concurso"`
		SomaNumeros int `json:"soma_numeros"`
	}

	type SomaHistoricaTemp struct {
		Concurso    string `json:"concurso"`
		SomaNumeros int    `json:"soma_numeros"`
	}

	// Chama o script Python para fazer a previsão
	cmd := exec.Command("C:\\Users\\Cid\\anaconda3\\python.exe", "../ai/lotofacil/soma.py")

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

	// Estrutura temporária para capturar concursos como string
	var tempSomas []SomaHistoricaTemp

	// Exibir saída do script
	fmt.Println("Saída do script Python:", out.String())

	err = json.Unmarshal(out.Bytes(), &tempSomas)
	if err != nil {
		fmt.Println("Erro ao converter JSON: %v", err)
		c.JSON(500, gin.H{"error": "Erro ao converter JSON"})
		return
	}

	// Converter Concurso de string para int
	var somas []SomaHistorica
	for _, temp := range tempSomas {
		concursoInt, err := strconv.Atoi(temp.Concurso)
		if err != nil {
			fmt.Println("Erro ao converter Concurso para int:", err)
			continue
		}
		somas = append(somas, SomaHistorica{
			Concurso:    concursoInt,
			SomaNumeros: temp.SomaNumeros,
		})
	}

	// Ordenar pelo campo Concurso
	sort.Slice(somas, func(i, j int) bool {
		return somas[i].Concurso < somas[j].Concurso
	})

	c.JSON(200, gin.H{
		"somas": somas,
	})
}
func consecutivosHandler(c *gin.Context) {

	type Consecutivos struct {
		Concurso     int `json:"concurso"`
		Consecutivos int `json:"consecutivos"`
	}

	type ConsecutivosTemp struct {
		Concurso     string `json:"concurso"`
		Consecutivos int    `json:"consecutivos"`
	}

	// Chama o script Python para fazer a previsão
	cmd := exec.Command("C:\\Users\\Cid\\anaconda3\\python.exe", "../ai/lotofacil/consecutivos.py")

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

	// Estrutura temporária para capturar concursos como string
	var tempConsecutivos []ConsecutivosTemp

	// Exibir saída do script
	fmt.Println("Saída do script Python:", out.String())

	err = json.Unmarshal(out.Bytes(), &tempConsecutivos)
	if err != nil {
		fmt.Println("Erro ao converter JSON: %v", err)
		c.JSON(500, gin.H{"error": "Erro ao converter JSON"})
		return
	}

	// Converter Concurso de string para int
	var consecutivos []Consecutivos
	for _, temp := range tempConsecutivos {
		concursoInt, err := strconv.Atoi(temp.Concurso)
		if err != nil {
			fmt.Println("Erro ao converter Concurso para int:", err)
			continue
		}
		consecutivos = append(consecutivos, Consecutivos{
			Concurso:     concursoInt,
			Consecutivos: temp.Consecutivos,
		})
	}

	// Ordenar pelo campo Concurso
	sort.Slice(consecutivos, func(i, j int) bool {
		return consecutivos[i].Concurso < consecutivos[j].Concurso
	})

	c.JSON(200, gin.H{
		"consecutivos": consecutivos,
	})
}
func probabilidadeHandler(c *gin.Context) {
	type Probabilidade struct {
		Numero        int     `json:"numero"`
		Probabilidade float32 `json:"probabilidade"`
	}
	// Chama o script Python para fazer a previsão
	cmd := exec.Command("C:\\Users\\Cid\\anaconda3\\python.exe", "../ai/lotofacil/probabilidade_numero.py")

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

	// Estrutura temporária para capturar JSON como map[string]float32
	var tempProbabilidades map[string]float32

	// Exibir saída do script
	fmt.Println("Saída do script Python:", out.String())

	err = json.Unmarshal(out.Bytes(), &tempProbabilidades)
	if err != nil {
		fmt.Println("Erro ao converter JSON: %v", err)
		c.JSON(500, gin.H{"error": "Erro ao converter JSON"})
		return
	}

	// Converter para slice de structs
	var probabilidades []Probabilidade
	for key, value := range tempProbabilidades {
		numeroInt, err := strconv.Atoi(key)
		if err != nil {
			fmt.Println("Erro ao converter Número para int:", err)
			continue
		}
		probabilidades = append(probabilidades, Probabilidade{
			Numero:        numeroInt,
			Probabilidade: value,
		})
	}

	// Ordenar pelo número
	sort.Slice(probabilidades, func(i, j int) bool {
		return probabilidades[i].Numero < probabilidades[j].Numero
	})

	c.JSON(200, gin.H{
		"probabilidades": probabilidades,
	})
}
func acertostHandler(c *gin.Context) {
	var input InputData
	// Decodifica os dados de entrada
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	// Chama o script Python para fazer a previsão
	numbers := strings.Trim(strings.Join(strings.Fields(fmt.Sprint(input.Numbers)), ","), "[]")
	concurso := input.Concurso
	concatenated := fmt.Sprintf("%d%s", numbers, concurso)
	cmd := exec.Command("C:\\Users\\Cid\\anaconda3\\python.exe", "../ai/lotofacil/acertos_concurso.py", concatenated)
	fmt.Println(concatenated)
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

	acertos := strings.TrimSpace(out.String())     // Remover espaços extras
	acertosNummeros := strings.Split(acertos, ",") // Separar por vírgula
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
		"acertos": acertosNummeros,
	})

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
	r.GET("/sorteios", getUltimosSorteios)                           // Lista os últimos sorteios
	r.GET("/sorteios/:concurso", getSorteioPorConcurso)              // Busca um concurso específico
	r.GET("/sorteios/stats/sorteados", getNumerosMaisMenosSorteados) // Retorna os números mais e menos sorteados
	r.POST("/predict", predictHandler)
	r.GET("/lotofacil/frequencias", frequenciasHandler)
	r.GET("/lotofacil/parImpar", parImparHandler)
	r.GET("/lotofacil/faixas", faixasHandler)
	r.GET("/lotofacil/somas", somaHandler)
	r.GET("/lotofacil/consecutivos", consecutivosHandler)
	r.GET("/lotofacil/probabilidades", probabilidadeHandler)
	r.POST("/lotofacil/acertos", acertostHandler)
	// Inicia o servidor na porta 8080
	r.Run(":8080")
}
