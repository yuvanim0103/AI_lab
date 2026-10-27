
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Scanner;
/**
 * AI Personal Study Assistant
 * A console based smart assistant that
 *  - tracks subjects, difficulty and exam dates,
 *  - generates a priority based daily study plan (rule based AI),
 *  - conducts a flashcard quiz and scores the student,
 *  - answers study related questions using keyword intent matching,
 *  - shows a progress report.
 */
public class AIStudyAssistant {
    // ---------- Model ---------
    static class Subject {
        String name;
        int difficulty;      // 1 (easy) to 5 (hard)
        int daysLeft;        // days left for the exam
        double hoursStudied; // total hours studied so far
        Subject(String name, int difficulty, int daysLeft) {
            this.name = name;
            this.difficulty = difficulty;
            this.daysLeft = daysLeft;
        }
        double targetHours() { return difficulty * 10.0; }
        double progress() {
            return Math.min(100.0, hoursStudied / targetHours() * 100.0);
        }
    }
    private final List<Subject> subjects = new ArrayList<>();
    private final Map<String, String> flashcards = new LinkedHashMap<>();   // question -> keyword answer
    private final Map<String, String> knowledge = new LinkedHashMap<>();    // keyword -> advice
    private final Scanner sc = new Scanner(System.in);
    public AIStudyAssistant() {
        loadFlashcards();
        loadKnowledge();
    }
    private void loadFlashcards() {
        flashcards.put("Which OOP concept hides data using private fields?", "encapsulation");
        flashcards.put("Which Java collection stores key-value pairs?", "map");
        flashcards.put("Which keyword is used to inherit a class in Java?", "extends");
        flashcards.put("What does JVM stand for?", "java virtual machine");
    }
    private void loadKnowledge() {
        knowledge.put("tired", "Take a 10 minute break, drink water and do light stretching. Sleep 7-8 hours.");
        knowledge.put("focus", "Use the Pomodoro method: 25 minutes study + 5 minutes break. Keep your phone away.");
        knowledge.put("remember", "Use active recall and spaced revision: revise after 1 day, 3 days and 7 days.");
        knowledge.put("formulas", "Write formulas on flash cards and practise problems daily instead of only reading.");
        knowledge.put("exam", "Solve previous year papers, revise weak topics first and avoid last minute new topics.");
        knowledge.put("stress", "Break the syllabus into small tasks, take deep breaths and talk to a friend or mentor.");
        knowledge.put("procrastinate", "Start with just 5 minutes. Beginning is the hardest part; momentum will follow.");
        knowledge.put("hello", "Hello! I am your AI study assistant. Ask me about focus, exams, memory or stress.");
    }
    // ---------- Input helpers ---------
    private String ask(String prompt) {
        System.out.print(prompt);
        return sc.nextLine().trim();
    }
    private int askInt(String prompt) {
        try {
            return Integer.parseInt(ask(prompt));
        } catch (NumberFormatException e) {
            return -1;
        }
    }
    private double askDouble(String prompt) {
        try {
            return Double.parseDouble(ask(prompt));
        } catch (NumberFormatException e) {
            return -1;
        }
    }
    private Subject find(String name) {
        for (Subject s : subjects) {
            if (s.name.equalsIgnoreCase(name)) return s;
        }
        return null;
    }
    // ---------- Features ---------
    void addSubject() {
        String name = ask("Enter subject name: ");
        int diff = askInt("Enter difficulty (1-5): ");
        int days = askInt("Enter days left for exam: ");
        if (name.isEmpty() || find(name) != null) {
            System.out.println("Invalid or duplicate subject name.");
        } else if (diff < 1 || diff > 5) {
            System.out.println("Difficulty must be between 1 and 5.");
        } else if (days < 1) {
            System.out.println("Days left must be at least 1.");
        } else {
            subjects.add(new Subject(name, diff, days));
            System.out.println("Subject '" + name + "' added.");
        }
    }
    void viewSubjects() {
        if (subjects.isEmpty()) {
            System.out.println("No subjects added yet.");
            return;
        }
        System.out.println("---------------------------------------------------------");
        System.out.printf("%-18s %-11s %-10s %-10s %s%n", "Subject", "Difficulty", "Days Left", "Studied", "Target");
        System.out.println("---------------------------------------------------------");
        for (Subject s : subjects) {
            System.out.printf("%-18s %-11d %-10d %-10.1f %.0f hrs%n",
                    s.name, s.difficulty, s.daysLeft, s.hoursStudied, s.targetHours());
        }
        System.out.println("---------------------------------------------------------");
    }
    // AI step: priority = difficulty weight + exam urgency + remaining syllabus
    void generatePlan() {
        if (subjects.isEmpty()) {
            System.out.println("Add subjects first.");
            return;
        }
        double available = askDouble("Enter hours available per day: ");
        if (available <= 0 || available > 16) {
            System.out.println("Please enter hours between 0 and 16.");
            return;
        }
        int n = subjects.size();
        double[] priority = new double[n];
        double total = 0;
        for (int i = 0; i < n; i++) {
            Subject s = subjects.get(i);
            priority[i] = s.difficulty * 2.0 + 30.0 / s.daysLeft + (100 - s.progress()) / 25.0;
            total += priority[i];
        }
        Integer[] order = new Integer[n];
        for (int i = 0; i < n; i++) order[i] = i;
        Arrays.sort(order, (a, b) -> Double.compare(priority[b], priority[a]));
        System.out.println("---------------------------------------------------------------");
        System.out.printf("%-5s %-18s %-9s %-10s %-10s %s%n", "Rank", "Subject", "Priority", "Hours/Day", "Pomodoros", "Level");
        System.out.println("---------------------------------------------------------------");
        int rank = 1;
        for (int idx : order) {
            Subject s = subjects.get(idx);
            double share = priority[idx] / total;
            double hours = available * share;
            int pomodoros = (int) Math.round(hours * 60 / 25.0);
            String level = share >= 0.35 ? "HIGH" : (share >= 0.20 ? "MEDIUM" : "LOW");
            System.out.printf("%-5d %-18s %-9.2f %-10.2f %-10d %s%n",
                    rank++, s.name, priority[idx], hours, pomodoros, level);
        }
        System.out.println("---------------------------------------------------------------");
        Subject top = subjects.get(order[0]);
        System.out.println("Suggestion: Start your day with '" + top.name + "' while your mind is fresh.");
        for (Subject s : subjects) {
            if (s.daysLeft <= 7) {
                System.out.println("ALERT: '" + s.name + "' exam is in " + s.daysLeft + " day(s). Revise now!");
            }
        }
    }
    void logSession() {
        String name = ask("Enter subject studied: ");
        double hours = askDouble("Enter hours studied: ");
        Subject s = find(name);
        if (s == null) {
            System.out.println("Subject '" + name + "' not found.");
        } else if (hours <= 0 || hours > 16) {
            System.out.println("Invalid hours.");
        } else {
            s.hoursStudied += hours;
            System.out.printf("Logged %.1f hours for %s. Progress: %.0f%%%n", hours, s.name, s.progress());
        }
    }
    void takeQuiz() {
        System.out.println("---- Flashcard Quiz (" + flashcards.size() + " questions) ----");
        int score = 0, q = 1;
        for (Map.Entry<String, String> card : flashcards.entrySet()) {
            System.out.println("Q" + q + ". " + card.getKey());
            String ans = ask("Your answer: ").toLowerCase();
            if (ans.contains(card.getValue())) {
                System.out.println("Correct!");
                score++;
            } else {
                System.out.println("Wrong. Correct answer: " + card.getValue());
            }
            q++;
        }
        double pct = score * 100.0 / flashcards.size();
        System.out.printf("Quiz score: %d/%d (%.0f%%)%n", score, flashcards.size(), pct);
        if (pct >= 75) System.out.println("Feedback: Excellent work! Keep it up.");
        else if (pct >= 50) System.out.println("Feedback: Good effort. Revise the missed topics.");
        else System.out.println("Feedback: Needs improvement. Revise the basics again.");
    }
    void askAssistant() {
        String text = ask("Ask the assistant: ").toLowerCase();
        List<String> words = Arrays.asList(text.split("[^a-z]+"));
        for (Map.Entry<String, String> e : knowledge.entrySet()) {
            if (words.contains(e.getKey())) {
                System.out.println("Assistant: " + e.getValue());
                return;
            }
        }
        System.out.println("Assistant: I am not sure about that. Try asking about focus, exam, remember, stress or tired.");
    }
    void progressReport() {
        if (subjects.isEmpty()) {
            System.out.println("No data available.");
            return;
        }
        System.out.println("------------- PROGRESS REPORT -------------");
        double sum = 0;
        for (Subject s : subjects) {
            int filled = (int) Math.round(s.progress() / 10.0);
        }
            String bar = "#".repeat(filled) + ".".repeat(10 - filled);
            System.out.printf("%-18s [%s] %3.0f%%%n", s.name, bar, s.progress());
            sum += s.progress();
        double avg = sum / subjects.size();
        System.out.printf("Overall progress: %.1f%%%n", avg);
        Subject weakest = subjects.get(0);
        for (Subject s : subjects) {
            if (s.progress() < weakest.progress()) weakest = s;
        }
        System.out.println("Needs most attention: " + weakest.name);
    }
    // ---------- Main ---------
    public static void main(String[] args) {
        AIStudyAssistant app = new AIStudyAssistant();
        int choice;
        do {
            System.out.println("\n====== AI PERSONAL STUDY ASSISTANT ======");
            System.out.println("1. Add Subject");
            System.out.println("2. View Subjects");
            System.out.println("3. Generate Smart Study Plan");
            System.out.println("4. Log Study Session");
            System.out.println("5. Take Flashcard Quiz");
            System.out.println("6. Ask the Assistant");
            System.out.println("7. Progress Report");
            System.out.println("8. Exit");
            choice = app.askInt("Enter your choice: ");
            switch (choice) {
                case 1: app.addSubject(); break;
                case 2: app.viewSubjects(); break;
                case 3: app.generatePlan(); break;
                case 4: app.logSession(); break;
                case 5: app.takeQuiz(); break;
                case 6: app.askAssistant(); break;
                case 7: app.progressReport(); break;
                case 8: System.out.println("Good luck with your studies! Goodbye."); break;
                default: System.out.println("Invalid choice. Try again.");
            }
        } while (choice != 8);
    }
}
