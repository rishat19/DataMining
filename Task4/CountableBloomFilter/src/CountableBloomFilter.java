public class CountableBloomFilter<T> {

    private final Double precision;
    private final int[] array;
    private final HashFunction<T>[] hashFunctions;

    public CountableBloomFilter(Double precision, int amountOfObjects, int capacity) {
        int i = 1;
        double tempPrecision = 1;
        while (precision.compareTo(tempPrecision) < 0) {
            tempPrecision = Math.pow((1 - Math.pow(Math.E, (-1.0 * i * amountOfObjects / capacity))), i);
            i++;
            if (i > capacity) {
                throw new IllegalStateException("Can't achieve this kind of precision.");
            }
        }
        this.precision = tempPrecision;
        this.array = new int[capacity];
        this.hashFunctions = new HashFunction[i];
        for (int j = 0; j < i; j++) {
            this.hashFunctions[j] = new HashFunction<>();
        }
    }

    public void add(T element) {
        for (HashFunction<T> hashFunction : hashFunctions) {
            array[Math.abs(hashFunction.hash(element)) % array.length]++;
        }
    }

    public boolean contains(T element) {
        for (HashFunction<T> hashFunction : hashFunctions) {
            if (array[Math.abs(hashFunction.hash(element)) % array.length] == 0) {
                return false;
            }
        }
        return true;
    }

    public Double getPrecision() {
        return precision;
    }
}
