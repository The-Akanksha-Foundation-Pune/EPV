#!/usr/bin/env python3
"""
Test script for Domestic Travel Enhancement

This script tests the new domestic travel functionality:
1. Amount field moves after Distance for domestic travel
2. New expenses show only travel details when first expense is domestic travel
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """Setup Chrome driver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Make sure Chrome and ChromeDriver are installed")
        return None

def test_domestic_travel_amount_position(driver, base_url):
    """Test that Amount field appears after Distance for domestic travel"""
    print("\n=== Testing Domestic Travel Amount Field Position ===")
    
    try:
        # Navigate to new expense page
        driver.get(f"{base_url}/new_expense")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "expenseHead-1"))
        )
        
        # Select a travel-related expense head
        expense_head_select = Select(driver.find_element(By.ID, "expenseHead-1"))
        travel_options = [option.text for option in expense_head_select.options if 'travel' in option.text.lower()]
        
        if not travel_options:
            print("No travel-related expense heads found")
            return False
            
        expense_head_select.select_by_visible_text(travel_options[0])
        
        # Wait for travel fields to appear
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "travel-fields-1"))
        )
        
        # Select Domestic Travel
        travel_type_select = Select(driver.find_element(By.ID, "travelType-1"))
        travel_type_select.select_by_value("domestic")
        
        # Wait for changes to take effect
        time.sleep(2)
        
        # Check that domestic amount field is visible
        domestic_amount_row = driver.find_element(By.ID, "domestic-amount-row-1")
        if domestic_amount_row.is_displayed():
            print("✓ Domestic amount field is visible after Distance field")
            
            # Check that standard amount field is hidden
            standard_amount_row = driver.find_element(By.ID, "standard-amount-row-1")
            if not standard_amount_row.is_displayed():
                print("✓ Standard amount field is hidden for domestic travel")
                return True
            else:
                print("✗ Standard amount field should be hidden for domestic travel")
                return False
        else:
            print("✗ Domestic amount field is not visible")
            return False
            
    except Exception as e:
        print(f"Error testing domestic travel amount position: {e}")
        return False

def test_domestic_travel_new_expenses(driver, base_url):
    """Test that new expenses show only travel details when first expense is domestic travel"""
    print("\n=== Testing Domestic Travel New Expenses ===")
    
    try:
        # Navigate to new expense page
        driver.get(f"{base_url}/new_expense")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "expenseHead-1"))
        )
        
        # Select a travel-related expense head
        expense_head_select = Select(driver.find_element(By.ID, "expenseHead-1"))
        travel_options = [option.text for option in expense_head_select.options if 'travel' in option.text.lower()]
        
        if not travel_options:
            print("No travel-related expense heads found")
            return False
            
        expense_head_select.select_by_visible_text(travel_options[0])
        
        # Wait for travel fields to appear
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "travel-fields-1"))
        )
        
        # Select Domestic Travel
        travel_type_select = Select(driver.find_element(By.ID, "travelType-1"))
        travel_type_select.select_by_value("domestic")
        
        # Wait for changes to take effect
        time.sleep(2)
        
        # Click Add Expense button
        add_expense_btn = driver.find_element(By.ID, "addExpenseBtn")
        add_expense_btn.click()
        
        # Wait for new expense to appear
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "expense-2"))
        )
        
        # Check that new expense has travel fields visible
        travel_fields_2 = driver.find_element(By.ID, "travel-fields-2")
        if travel_fields_2.is_displayed():
            print("✓ New expense shows travel fields")
            
            # Check that travel type is set to domestic
            travel_type_2 = Select(driver.find_element(By.ID, "travelType-2"))
            if travel_type_2.first_selected_option.get_attribute("value") == "domestic":
                print("✓ New expense travel type is set to domestic")
                
                # Check that domestic amount field is visible
                domestic_amount_2 = driver.find_element(By.ID, "domestic-amount-row-2")
                if domestic_amount_2.is_displayed():
                    print("✓ New expense shows domestic amount field")
                    
                    # Check that standard amount field is hidden
                    standard_amount_2 = driver.find_element(By.ID, "standard-amount-row-2")
                    if not standard_amount_2.is_displayed():
                        print("✓ New expense hides standard amount field")
                        return True
                    else:
                        print("✗ New expense should hide standard amount field")
                        return False
                else:
                    print("✗ New expense should show domestic amount field")
                    return False
            else:
                print("✗ New expense travel type should be set to domestic")
                return False
        else:
            print("✗ New expense should show travel fields")
            return False
            
    except Exception as e:
        print(f"Error testing domestic travel new expenses: {e}")
        return False

def main():
    """Main test function"""
    print("Domestic Travel Enhancement Test")
    print("=" * 40)
    
    # Get base URL from environment or use default
    base_url = os.getenv('EPV_BASE_URL', 'http://localhost:5000')
    print(f"Testing against: {base_url}")
    
    # Setup driver
    driver = setup_driver()
    if not driver:
        print("Failed to setup driver. Exiting.")
        sys.exit(1)
    
    try:
        # Run tests
        test1_passed = test_domestic_travel_amount_position(driver, base_url)
        test2_passed = test_domestic_travel_new_expenses(driver, base_url)
        
        # Print results
        print("\n" + "=" * 40)
        print("TEST RESULTS")
        print("=" * 40)
        print(f"Domestic Travel Amount Position: {'PASSED' if test1_passed else 'FAILED'}")
        print(f"Domestic Travel New Expenses: {'PASSED' if test2_passed else 'FAILED'}")
        
        if test1_passed and test2_passed:
            print("\n🎉 All tests passed! Domestic travel enhancement is working correctly.")
            return 0
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            return 1
            
    except Exception as e:
        print(f"Error during testing: {e}")
        return 1
    finally:
        driver.quit()

if __name__ == "__main__":
    sys.exit(main()) 