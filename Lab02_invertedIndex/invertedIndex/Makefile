# Nombre del ejecutable
TARGET := invertedIndex

# Directorios
SRC_DIR := src
INC_DIR := include
OBJ_DIR := obj

# Compilador y flags
CXX := g++
CXXFLAGS := -O2 -std=c++17 -pthread -I$(INC_DIR)

# Archivos fuente
SRCS := $(wildcard $(SRC_DIR)/*.cpp)

# Archivos objeto
OBJS := $(patsubst $(SRC_DIR)/%.cpp, $(OBJ_DIR)/%.o, $(SRCS))

# Regla principal
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

# Compilar .cpp a .o
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp | $(OBJ_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Crear carpeta obj si no existe
$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

# Limpiar archivos generados
.PHONY: clean
clean:
	rm -rf $(OBJ_DIR) $(TARGET)
