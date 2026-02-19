# Login & Dashboard System - Documentation.

This project contains a Java Swing application with MySQL database connectivity, featuring separate dashboards for Admins and Users.

## 1. Database Connection (`DBConnect.java`)

Create a file named `DBConnect.java` and paste the following code to handle the MySQL connection.

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DBConnect {
    private static final String URL = "jdbc:mysql://localhost:3306/login_db";
    private static final String USER = "root";
    private static final String PASS = "";

    public static Connection getConnection(){
        try {
            return DriverManager.getConnection(URL, USER, PASS);
        } catch(SQLException e) {
            e.printStackTrace();
            return null;
        }
    }
}

```

---

## 2. Login Form Logic

The following snippets belong inside your **LOGIN FORM** class.

### Login Button (`btnLogin`)

Handles user authentication and role-based redirection.

- **Username Field:** `uname`
- **Password Field:** `upass`

```java
private void btnLoginActionPerformed(java.awt.event.ActionEvent evt) {
    String username = uname.getText().trim();
    String password = String.valueOf(upass.getPassword()).trim();

    if (username.isEmpty() || password.isEmpty()) {
        JOptionPane.showMessageDialog(this, "Please fill all fields");
        return;
    }

    // Updated SQL to get role, fname, and lname
    String sql = "SELECT role, fname, lname FROM users WHERE username = ? AND password = ?";

    try (java.sql.Connection con = DBConnect.getConnection()) {
        if (con == null) {
            JOptionPane.showMessageDialog(this, "Database Connection Failed!");
            return;
        }

        try (java.sql.PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setString(1, username);
            ps.setString(2, password);

            try (java.sql.ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    // Get role and names
                    String role = rs.getString("role").trim();
                    String fname = rs.getString("fname").trim();
                    String lname = rs.getString("lname").trim();

                    System.out.println("Role: [" + role + "], Name: [" + fname + " " + lname + "]");

                    if (role.equalsIgnoreCase("Admin")) {
                        // Redirect to admin dashboard and pass names
                        dashboard adminDash = new dashboard(fname, lname);
                        adminDash.setLocationRelativeTo(null);
                        adminDash.setVisible(true);
                        this.dispose();
                    } else if (role.equalsIgnoreCase("User")) {
                        // Redirect to user dashboard and pass names
                        udashboard userDash = new udashboard(fname, lname);
                        userDash.setLocationRelativeTo(null);
                        userDash.setVisible(true);
                        this.dispose();
                    } else {
                        JOptionPane.showMessageDialog(this, "Unknown role. Contact admin.");
                    }
                } else {
                    JOptionPane.showMessageDialog(this, "Invalid Username or Password");
                }
            }
        }
    } catch (Exception e) {
        JOptionPane.showMessageDialog(this, "Database Error: " + e.getMessage());
        e.printStackTrace();
    }
}

```

### Exit Button (`btnExit`)

```java
private void btnExitActionPerformed(java.awt.event.ActionEvent evt) {
    int choice = JOptionPane.showConfirmDialog(
        this,
        "Are you sure you want to exit?",
        "Exit Confirmation",
        JOptionPane.YES_NO_OPTION,
        JOptionPane.QUESTION_MESSAGE
    );
    if (choice == JOptionPane.YES_OPTION) {
        System.exit(0);
    }
}

```

### Signup Button (`btnSignup`)

```java
private void btnSignupActionPerformed(java.awt.event.ActionEvent evt) {
    Signup sg = new Signup();
    sg.setLocationRelativeTo(null);
    sg.setVisible(true);
    this.dispose();
}

```

---

## 3. Dashboard Forms

These constructors update the welcome message and display a real-time clock.

### Admin Dashboard (`dashboard.java`)

- **Label Names:** `lblWelcome`, `time`

```java
public dashboard(String fname, String lname) {
    initComponents();
    lblWelcome.setText("Welcome, " + fname + " " + lname);
    javax.swing.Timer timer = new javax.swing.Timer(1000, e -> {
        java.time.LocalDateTime now = java.time.LocalDateTime.now();
        java.time.format.DateTimeFormatter formatter = java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        time.setText(now.format(formatter));
    });
    timer.start();
}

```

### User Dashboard (`udashboard.java`)

```java
public udashboard(String fname, String lname) {
    initComponents();
    lblWelcome.setText("Welcome, " + " " + lname);
    javax.swing.Timer timer = new javax.swing.Timer(1000, e -> {
        java.time.LocalDateTime now = java.time.LocalDateTime.now();
        java.time.format.DateTimeFormatter formatter = java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        time.setText(now.format(formatter));
    });
    timer.start();
}

```

---

## 4. Signup Form Logic

These snippets belong inside your **Signup** class.

### Register Button (`btnRegister`)

Handles user registration by inserting new records into the database.

- **Variables:** `uname`, `upass`, `fname`, `mname`, `lname`, `urole`
- **Database Utility:** Uses `DBConnect.getConnection()`

```java
private void btnRegisterActionPerformed(java.awt.event.ActionEvent evt) {
    // TODO add your handling code here:
    String username = uname.getText().trim();
    String password = String.valueOf(upass.getPassword()).trim();
    String firstname = fname.getText().trim();
    String middlename = mname.getText().trim();
    String lastname = lname.getText().trim();
    String role = urole.getSelectedItem().toString();

    if (username.isEmpty() || password.isEmpty()) {
        JOptionPane.showMessageDialog(this, "Fill all fields");
        return;
    }

    String sql = "INSERT INTO users(username, password, fname, mname, lname, role) VALUES(?,?,?,?,?,?)";

    // Use try-with-resources to automatically close resources
    try (java.sql.Connection con = DBConnect.getConnection();
         java.sql.PreparedStatement ps = con.prepareStatement(sql)) {

        if (con == null) {
            JOptionPane.showMessageDialog(this, "Database connection failed!");
            return;
        }

        ps.setString(1, username);
        ps.setString(2, password);
        ps.setString(3, firstname);
        ps.setString(4, middlename);
        ps.setString(5, lastname);
        ps.setString(6, role);

        int rowsInserted = ps.executeUpdate();

        if (rowsInserted > 0) {
            JOptionPane.showMessageDialog(this, "Registration Successful!");

            Login login = new Login();
            login.setLocationRelativeTo(null); // center on screen
            login.setVisible(true);
            this.dispose();

            // Clear fields after successful registration
            uname.setText("");
            upass.setText("");
            fname.setText("");
            mname.setText("");
            lname.setText("");
            urole.setSelectedIndex(0);
        } else {
            JOptionPane.showMessageDialog(this, "Registration Failed!");
        }
    } catch (Exception e) {
        e.printStackTrace();
        JOptionPane.showMessageDialog(this, "Error Saving Data: " + e.getMessage());
    }
}

```

### Back Button (`btnBack`)

Returns the user to the Login screen.

```java
private void btnBackActionPerformed(java.awt.event.ActionEvent evt) {
    // TODO add your handling code here:
    Login log = new Login();
    log.setVisible(true);
    this.dispose();
}

```
