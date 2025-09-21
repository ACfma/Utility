#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

#define MAX_WORD_LENGTH 100
#define DEFAULT_THRESHOLD 0.8

// Structure to hold configuration options
typedef struct {
	int use_transposition;
	int use_jaro;
	float threshold;
} Config;

// Initialize configuration with defaults
Config config = {
	.use_transposition = 1,
	.use_jaro = 0,
	.threshold = DEFAULT_THRESHOLD
};

// Calculate the Damerau-Levenshtein distance with optional transposition
int damerau_levenshtein_distance(const char *str1, const char *str2) {
	int m = strlen(str1);
	int n = strlen(str2);
	int **dp = (int **)malloc((m + 1) * sizeof(int *));

	// Initialize matrix
	for (int i = 0; i <= m; i++) {
		dp[i] = (int *)malloc((n + 1) * sizeof(int));
		dp[i][0] = i;
	}
	for (int j = 0; j <= n; j++){
		dp[0][j] = j;
	}
	
	// Fill the matrix
	for (int i = 1; i <= m; i++) {
		for (int j = 1; j <= n; j++) {
			if (str1[i-1] == str2[j-1])
				dp[i][j] = dp[i-1][j-1];
	    		else {
				int cost = 1;
				int deletion = dp[i-1][j] + cost;
				int insertion = dp[i][j-1] + cost;
				int substitution = dp[i-1][j-1] + cost;

				// Handle transposition if enabled
				if (config.use_transposition && 
				    i > 1 && j > 1 && 
				    str1[i-1] == str2[j-2] && 
				    str1[i-2] == str2[j-1]) {
				    dp[i][j] = ((deletion < insertion ? deletion : insertion) < substitution ? 
					       (deletion < insertion ? deletion : insertion) : substitution);
				    dp[i][j] = (dp[i][j] < (dp[i-2][j-2] + cost)) ? dp[i][j] : (dp[i-2][j-2] + cost);
				} else {
				    dp[i][j] = ((deletion < insertion ? deletion : insertion) < substitution ? 
					       (deletion < insertion ? deletion : insertion) : substitution);
				}
		    	}
		}
	}

	int distance = dp[m][n];
	
	// Free allocated memory
	for (int i = 0; i <= m; i++){
		free(dp[i]);
	}
	free(dp);

	return distance;
}

// Calculate Jaro similarity
float jaro_similarity(const char *str1, const char *str2) {
	int len1 = strlen(str1);
	int len2 = strlen(str2);
	
	if (len1 == 0 && len2 == 0) return 1.0;
	if (len1 == 0 || len2 == 0) return 0.0;

	int match_distance = (fmax(len1, len2) / 2) - 1;
	int matches1[len1], matches2[len2];
	int k, matches = 0;
	int transpositions = 0;

	// Initialize arrays
	memset(matches1, 0, sizeof(int) * len1);
	memset(matches2, 0, sizeof(int) * len2);

	// Find matching characters
	for (int i = 0; i < len1; i++) {
		for (k = fmax(0, i-match_distance); k < fmin(i+match_distance+1, len2); k++) {
			if (str1[i] == str2[k] && matches2[k] == 0) {
				matches1[i] = 1;
				matches2[k] = 1;
				matches++;
				break;
			}
		}
	} 
	
	if (matches == 0) return 0.0;
	
	
	// Count transpositions
	k = 0;
	for (int i = 0; i < len1; i++) {
		if (matches1[i]) {
			while (!matches2[k]) k++;
			if (str1[i] != str2[k]) transpositions++;
			k++;
		}
	}

	// Calculate Jaro similarity
	float common_chars = matches / (float)len1;
	float common_chars2 = matches / (float)len2;
	float half_transpositions = transpositions / 2.0;

	return (common_chars + common_chars2 + 
	   (matches - half_transpositions) / (float)matches) / 3.0;
}

// Convert string to lowercase
void to_lowercase(char *str) {
	for (; *str; str++)
		*str = tolower(*str);
}

// Calculate similarity ratio between two strings
float calculate_similarity(const char *str1, const char *str2) {
	if (config.use_jaro)
		return jaro_similarity(str1, str2);
    
	int max_length = (strlen(str1) > strlen(str2)) ? strlen(str1) : strlen(str2);
	int distance = damerau_levenshtein_distance(str1, str2);
	return 1.0 - ((float)distance / max_length);
}

// Find similar words in file given a target word
void find_similar_words(const char *filename, const char *target_word) {
	FILE *file = fopen(filename, "r");
	if (!file) {
		perror("Error opening file");
		return;
	}
    
	char word[MAX_WORD_LENGTH];
	char target_copy[MAX_WORD_LENGTH];
	unsigned int row_number=1;
	strcpy(target_copy, target_word);
	to_lowercase(target_copy);
	
	printf("Similar words (threshold >= %.2f):\n", config.threshold);
	printf("ROW NUMBER - SIMILARITY - RETRIEVED STRING\n");
	while (fscanf(file, "%99s", word) == 1) {
		char word_copy[MAX_WORD_LENGTH];
        	strcpy(word_copy, word);
        	to_lowercase(word_copy);
        	
		float similarity = calculate_similarity(target_copy, word_copy);
		if (similarity >= config.threshold && strcmp(word_copy, target_copy) != 0) {
		    printf("%u - %.2f - %s\n", row_number, similarity, word);
		}
		row_number++;
	}
	
	fclose(file);
}

int main(int argc, char *argv[]) {
	if (argc < 3 || argc > 6) {
		printf("Usage: %s filename word [options]\n", argv[0]);
		printf("Options:\n");
		printf("-t N    Set threshold (default %.2f)\n", DEFAULT_THRESHOLD);
		printf("-d      Disable transposition (Lavenshtein distance)\n");
		printf("-j      Use Jaro distance (faster but less precise)\n");
		return 1;
	}
    
    

	// Parse arguments
	int arg_index = 3;
	while (arg_index < argc) {
		if (strcmp(argv[arg_index], "-t") == 0 && arg_index + 1 < argc) {
	    		config.threshold = atof(argv[++arg_index]);
	    		if (config.threshold > 1) {
	    			printf("Threshold should be between 0 and 1!");
	    			return 1;
	    		}
		    	arg_index++;
		} else if (strcmp(argv[arg_index], "-d") == 0) {
		    	config.use_transposition = 0;
		    	arg_index++;
		} else if (strcmp(argv[arg_index], "-j") == 0) {
		    	config.use_jaro = 1;
		    	arg_index++;
		} else {
		    	break;
		}
	}
	
	printf("WARNING: Maximum string size allowed for search is 100 char!\n");
	
	find_similar_words(argv[1], argv[2]);

	return 0;
}
