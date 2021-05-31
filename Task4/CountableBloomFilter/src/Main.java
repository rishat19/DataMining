import java.io.*;
import java.util.ArrayList;
import java.util.Collections;

public class Main {

    public static void main(String[] args) {

        ArrayList<String> words = new ArrayList<>();

        try {
            BufferedReader bufferedReader = new BufferedReader(new FileReader(new File("src/Text")));
            String line;
            while ((line = bufferedReader.readLine()) != null) {
                String[] temp = line.trim().split("[\\s,\n!@#$%^&*().{}\\[\\]\"]+");
                Collections.addAll(words, temp);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        CountableBloomFilter<String> bloomFilter = new CountableBloomFilter<>(0.0001, words.size(), 18000);

        for (String word : words) {
            bloomFilter.add(word);
        }

        String[] checkList = {"data", "process", "gog", "use", "machine", "mining", "cat", "system", "form", "database"};

        for (String checkWord : checkList) {
            if (bloomFilter.contains(checkWord)) {
                System.out.println("Word \"" + checkWord + "\" was encountered with the probability of " + (1 - bloomFilter.getPrecision()));
            } else {
                System.out.println("Word \"" + checkWord + "\" 100% was not encountered");
            }
        }

    }

}
