import java.util.ArrayList;
import java.util.HashSet;

public class UniversalRomanNumber {

    private static String ROMAN_NUMERAL_ALPHABET = "-OIVXLCDM";
    private final static int MULTIPLY_CONST = 4;
    private final static int BASE_NUMBER = 10;
    private final static int MAX_DELTA = 2;
    private final static int MAX_DELTA_TRIPLET = 1;

    private ArrayList<Integer> values;
    private ArrayList<String> valuesInRoman;


    private String alphabet;
    private String romanNumber = null;
    private char zeroCharacter;
    private char minusCharacter;
    private boolean isNegative = false;


    public UniversalRomanNumber(final String alphabet){

        if(!isValidAlphabet(alphabet)){
            setDefaultValues();
            createLookUpTable();
            return;
        }

        minusCharacter = alphabet.charAt(0);
        zeroCharacter = alphabet.charAt(1);
        this.alphabet = alphabet.substring(2);
        createLookUpTable();
    }

    public UniversalRomanNumber(){
        setDefaultValues();
        createLookUpTable();
    }

    /**
     *
     * Returns used alphabet letters consisting of minus character, zero character and the alphabet
     *
     * @return string consisting of minus character, zero character and the alphabet
     */
    public String getRomanLetters(){
        return Character.toString(minusCharacter) + Character.toString(zeroCharacter) + alphabet;
    }

    /**
     *
     * Calculates and returns max integer that can be created with an alphabet provided in private variable alphabet.
     *
     * @return max integer that can be created with an alphabet provided in private variable alphabet
     */
    public int maximum(){
        if (alphabet.length() % 2 == 1){
            return MULTIPLY_CONST * indexToIntConversion(alphabet.length()-1) - 1;
        }
        return indexToIntConversion(alphabet.length()) - indexToIntConversion(alphabet.length()-2) - 1;
    }

    /**
     *
     *  Calculates and returns min integer using maximum().
     *
     * @return min integer that can be created with an alphabet provided in private variable alphabet
     */
    public int minimum(){
        return maximum() * -1;
    }

    /**
     * Sets internal romanNumber value to value provided in the parameter.
     * Checks if romanNumber is a valid numeral for an alphabet provided in private variable alphabet.
     * Also updates isNegative boolean flag accordingly.
     *
     * @param numeral a roman numeral
     * @return true if the operation was successful
     */
    public boolean setRomanNumber(final String numeral){
        if(numeral.isEmpty()){
            return false;
        }

        if(numeral.equals(Character.toString(minusCharacter) + Character.toString(zeroCharacter))){
            return false;
        }

        if(!isValidAlphabetNumeral(numeral)){
            return false;
        }

        if(numeral.charAt(0) == minusCharacter){
            isNegative = true;
            this.romanNumber = numeral.substring(1);
        }else{
            isNegative = false;
            this.romanNumber = numeral;
        }

        return true;
    }

    /**
     *
     * Calculates and returns integer representation of internal romanNumber value using romanToInt().
     *
     * @return zero or integer representation of private variable romanNumber
     */
    public int getValue(){
        if(this.romanNumber == null){
            return 0;
        }

        return isNegative ? romanToInt(this.romanNumber) * -1 : romanToInt(this.romanNumber);
    }

    /**
     * Returns string representing internal romanNumber.
     * Checks if romanNumber is not null and returns string representation of roman numeral stored in private variable romanNumber or zero string representation stored in private variable romanZero.
     *
     * @return string representation of zero or roman numeral stored in private variable romanNumber
     */
    public String getRomanNumber(){
        if(romanNumber == null){
            return Character.toString(zeroCharacter);
        }

        return isNegative ? Character.toString(minusCharacter) + romanNumber : romanNumber;
    }

    /**
     *
     * Sets internal romanNumber value to roman numeral representation using intToRoman() for conversion.
     * Checks if provided integer can be converted to roman numeral using alphabet in private variable alphabet.
     *
     * @param value integer that will be stored as a roman numeral
     * @return true if the operation was successful
     */
    public boolean setValue(int value){
        if (value < minimum() || value > maximum()){
            return false;
        }

        if(value == 0){
            romanNumber = Character.toString(zeroCharacter);
            return true;
        }

        romanNumber = intToRoman(value);
        return true;
    }

    /**
     * Creates lookup table for basic integer to roman numeral conversion and vice versa.
     */
    private void createLookUpTable(){
        values = new ArrayList<>();
        valuesInRoman = new ArrayList<>();

        values.add(1);
        valuesInRoman.add(Character.toString(alphabet.charAt(0)));

        for (int i = 1; i < alphabet.length(); i++) {

            if(i % 2 == 1){
                valuesInRoman.add(Character.toString(alphabet.charAt(i-1)) + Character.toString(alphabet.charAt(i)));
                int fours = romanLetterToIntByIndexFromLetters(alphabet, alphabet.charAt(i)) - romanLetterToIntByIndexFromLetters(alphabet, alphabet.charAt(i-1));
                values.add(fours);
            }

            if(i % 2 == 0){
                valuesInRoman.add(Character.toString(alphabet.charAt(i-2)) + Character.toString(alphabet.charAt(i)));
                int nines = romanLetterToIntByIndexFromLetters(alphabet, alphabet.charAt(i)) - romanLetterToIntByIndexFromLetters(alphabet, alphabet.charAt(i-2));
                values.add(nines);
            }

            valuesInRoman.add(Character.toString(alphabet.charAt(i)));
            values.add(romanLetterToIntByIndexFromLetters(alphabet, alphabet.charAt(i)));
        }
    }

    /**
     *
     * Converts integer to roman numeral.
     * Uses lookup table to convert each digit into roman numeral and returns roman numeral representation..
     *
     * @param value value to be converted into roman numeral using alphabet stored in private variable alphabet
     * @return roman numeral representation of provided value
     */
    private String intToRoman(final int value){

        int currentNumber = value;
        if(value < 0){
            isNegative = true;
            currentNumber *= -1;
        }else{
            isNegative = false;
        }

        StringBuilder sb = new StringBuilder();

        for (int i = values.size() -1 ; i >= 0; i--) {
            int times = currentNumber / values.get(i);
            currentNumber %= values.get(i);
            while(times >0){
                sb.append(valuesInRoman.get(i));
                times--;
            }
        }

        return sb.toString();
    }

    /**
     * Converts roman numeral to integer.
     * Calculates and returns integer value of roman numeral stored in private variable romanNumber.
     *
     * @param romanNumber roman numeral to be converted to integer
     * @return integer value of roman numeral stored in private variable romanNumber
     */
    private int romanToInt(final String romanNumber)
    {
        if(romanNumber.length() == 1){
            return romanLetterToIntByIndexFromLetters(alphabet, romanNumber.charAt(0));
        }

        int result = 0;
        char lastLetter =  romanNumber.charAt(romanNumber.length()-1);
        result+=romanLetterToIntByIndexFromLetters(alphabet, lastLetter);
        int secCounter =0;
        for (int i = romanNumber.length()-2; i >= 0; i--) {

            char curLetter = romanNumber.charAt(i);
            int curNumber = romanLetterToIntByIndexFromLetters(alphabet, curLetter);
            if( curNumber == romanLetterToIntByIndexFromLetters(alphabet, lastLetter))
            {
                result += curNumber;
                secCounter++;
            }
            else if( curNumber > romanLetterToIntByIndexFromLetters(alphabet, lastLetter))
            {
                secCounter = 0;
                result += curNumber;
            }
            else if( curNumber < romanLetterToIntByIndexFromLetters(alphabet, lastLetter))
            {
                secCounter = 0;
                result += (romanLetterToIntByIndexFromLetters(alphabet, lastLetter)-curNumber)-romanLetterToIntByIndexFromLetters(alphabet, lastLetter);
            }
            lastLetter = curLetter;
        }
        return result;
    }

    /**
     * Sets default values for alphabet, minus and zero representation.
     */
    private void setDefaultValues(){
        minusCharacter = ROMAN_NUMERAL_ALPHABET.charAt(0);
        zeroCharacter = ROMAN_NUMERAL_ALPHABET.charAt(1);
        this.alphabet = ROMAN_NUMERAL_ALPHABET.subSequence(2, ROMAN_NUMERAL_ALPHABET.length()).toString();
    }

    /**
     *
     * Checks if provided alphabet is valid. Only letters a-z (case-insensitive) and all characters must be unique to be valid alphabet.
     *
     * @param alphabet alphabet in string
     * @return true if provded alphabet is valid
     */
    private boolean isValidAlphabet(final String alphabet){
        if(alphabet.length() < 3){
            return false;
        }

        HashSet<Character> uniqueLetters = new HashSet<>();
        for (int i = 1; i < alphabet.length(); i++) {
            Character currentChar = alphabet.charAt(i);
            if(!uniqueLetters.contains(currentChar)){
                uniqueLetters.add(currentChar);
            }else{
                return false;
            }

        }

        for (int i = 1; i < alphabet.length(); i++) {
            Character currentChar = alphabet.charAt(i);
            if (!Character.isUpperCase(currentChar) || !Character.isLetter(currentChar)){
                return false;
            }
        }


        return true;
    }


    /**
     *
     * Calculates and returns integer value for i-th roman numeral character in the sequence, where i-th roman numeral is fromIndex.
     * E.g. indexToIntConversion(0) = 1, indexToIntConversion(1) = 5, indexToIntConversion(2) = 10, indexToIntConversion(3) = 50, ...
     *
     * @param fromIndex i-th roman numeral character in the sequence
     * @return integer value for i-th roman numeral character in the sequence
     */
    private int indexToIntConversion(final int fromIndex){
        int index = fromIndex;

        if(index % 2 == 1){
            index = (index-1) / 2;
            return (int) Math.pow(BASE_NUMBER, index) * 5;
        }

        index /=2;
        return (int) Math.pow(BASE_NUMBER, index);
    }

    /**
     *
     * Uses indexToIntConversion() to calculate integer value of character in the alphabet.
     *
     * @param alphabetLetters an alphabet that will be used to find value of character
     * @param character a character to find value of
     * @return value of character in the alphabet
     */
    public int romanLetterToIntByIndexFromLetters(final String alphabetLetters, final char character){
        return indexToIntConversion(alphabetLetters.indexOf(character));
    }

    /**
     *
     * Checks if inputNumeral contains only characters from alphabet, does not contain sequence of 4 same characters, contains only allowed sequences of pairs and triplets.
     *
     * @param inputNumeral an input numeral
     * @return true if is valid numeral for alphabet stored in private variable alphabet
     */
    private boolean isValidAlphabetNumeral(final String inputNumeral){
        String numeral = inputNumeral;

        if(inputNumeral.charAt(0) == minusCharacter){
            numeral = inputNumeral.substring(1);
        }

        if(!ContainsOnlyCharactersFromAlphabet(numeral)){
            return false;
        }

        //check 4same
        int counter = 1;
        char currentChar = numeral.charAt(0);
        for (int i = 1; i < numeral.length(); i++) {
            if(numeral.charAt(i) == currentChar){
                counter++;
            }else{
                counter = 0;
            }

            if(counter >= 4){
                return false;
            }
        }

        char currentGreatestCharacter = numeral.charAt(0);
        for (int i = 1; i < numeral.length(); i++) {
            int left = romanLetterToIntByIndexFromLetters(alphabet, currentGreatestCharacter);
            int right = romanLetterToIntByIndexFromLetters(alphabet, numeral.charAt(i));

            if (left > right || isValidPair(alphabet, currentGreatestCharacter, numeral.charAt(i))){
                currentGreatestCharacter = numeral.charAt(i);
            }else{
                return false;
            }

            if(i > 1 && !isValidTriplet(alphabet, numeral.charAt(i-2), numeral.charAt(i-1), numeral.charAt(i))){
                return false;
            }
        }
        return true;
    }

    /**
     *
     * Checks if given a pair of characters is valid pair for given alphabet.
     * E.g. for roman numeral alphabet, IV is allowed while VX is not allowed.
     *
     * @param alphabet an alphabet
     * @param left a first character of pair
     * @param right a second character of pair
     * @return if provided pair is valid pair for given alphabet
     */
    private boolean isValidPair(final String alphabet, final char left, final char right){
        int leftIndex = alphabet.indexOf(left);
        int rightIndex = alphabet.indexOf(right);

        boolean isLeftEven = leftIndex % 2 == 0;
        boolean isRightEven = rightIndex % 2 == 0;


        if(!isLeftEven && !isRightEven && left == right)
            return false;

        if(isLeftEven && leftIndex <= rightIndex &&  rightIndex - leftIndex <= MAX_DELTA){
            return true;
        }

        return false;
    }

    /**
     *
     * Checks if given a triplet of characters is valid triplet for given alphabet.
     * E.g. for roman numeral alphabet, XII is allowed while IIX is not allowed.
     *
     * @param alphabet an alphabet
     * @param first a first character of triplet
     * @param second a second character of triplet
     * @param third a third character of triplet
     * @return if provided triplet is valid triplet for given alphabet
     */
    private boolean isValidTriplet(final String alphabet,final char first, final char second, final char third){
        int leftIndex = alphabet.indexOf(first);
        int middleIndex = alphabet.indexOf(second);
        int rightIndex = alphabet.indexOf(third);

        if(middleIndex < rightIndex &&  leftIndex == middleIndex){
            return false;
        }

        if(leftIndex < middleIndex && middleIndex > rightIndex && middleIndex-rightIndex == MAX_DELTA_TRIPLET){
            return false;
        }

        if(leftIndex % 2 == 1 && rightIndex % 2 == 1 && first == third){
            return false;
        }

        if(leftIndex < middleIndex && middleIndex == rightIndex){
            return false;
        }

        return true;
    }

    /**
     *
     * Checks if the input numeral contains only chracters from the alphabet.
     *
     * @param numeral a numeral
     * @return true if numeral contains only characters from alphabet
     */
    private boolean ContainsOnlyCharactersFromAlphabet(final String numeral){
        for (int i = 0; i < numeral.length(); i++) {
            if(alphabet.indexOf(numeral.charAt(i)) == -1){
                return false;
            }
        }
        return true;
    }

}
