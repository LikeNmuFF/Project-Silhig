/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package main;

/**
 *
 * @author Hp
 */
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Connection;
public class DBConnect {
    private static final String URL = "jdbc:mysql://localhost:3306/login_db";
    private static final String USER = "root";
    private static final String PASS = "";
    
    public static Connection getConnection(){
        try {
            return DriverManager.getConnection(URL,USER,PASS);
        
        } catch(SQLException e) {
            e.printStackTrace();
            return null;
        }
    }
}
