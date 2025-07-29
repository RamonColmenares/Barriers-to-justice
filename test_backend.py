"""
Test script to verify the backend implementation works
"""
import sys
import os

# Add the current directory to the path so we can import from api
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

def test_data_loading():
    """Test data loading functionality"""
    try:
        from api.data_loader import load_data
        from api.models import cache
        
        print("🧪 Testing data loading...")
        
        # Test loading data
        success = load_data()
        
        if success:
            print("✅ Data loaded successfully")
            
            # Check what datasets are available
            juvenile_cases = cache.get('juvenile_cases')
            juvenile_history = cache.get('juvenile_history')
            proceedings = cache.get('proceedings')
            reps_assigned = cache.get('reps_assigned')
            lookup_decisions = cache.get('lookup_decisions')
            analysis_filtered = cache.get('analysis_filtered')
            
            print(f"📊 Juvenile cases: {len(juvenile_cases) if juvenile_cases is not None else 0}")
            print(f"📊 Juvenile history: {len(juvenile_history) if juvenile_history is not None else 0}")
            print(f"📊 Proceedings: {len(proceedings) if proceedings is not None else 0}")
            print(f"📊 Reps assigned: {len(reps_assigned) if reps_assigned is not None else 0}")
            print(f"📊 Lookup decisions: {len(lookup_decisions) if lookup_decisions is not None else 0}")
            print(f"📊 Analysis filtered: {len(analysis_filtered) if analysis_filtered is not None else 0}")
            
            return True
        else:
            print("❌ Data loading failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing data loading: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chart_generation():
    """Test chart generation functionality"""
    try:
        from api.chart_generator import generate_representation_outcomes_chart, generate_outcome_percentages_chart
        
        print("\n🧪 Testing chart generation...")
        
        # Test the main representation outcomes chart
        chart_data = generate_representation_outcomes_chart()
        
        if "error" in chart_data:
            print(f"❌ Chart generation failed: {chart_data['error']}")
            return False
        else:
            print("✅ Representation outcomes chart generated successfully")
            
            # Check if we have summary data
            if 'summary' in chart_data:
                summary = chart_data['summary']
                print(f"📈 Total cases in chart: {summary.get('total_cases', 0)}")
                print(f"📈 Count data: {summary.get('count_data', {})}")
                print(f"📈 Percentage data: {summary.get('percentage_data', {})}")
        
        # Test the percentage chart
        percentage_chart = generate_outcome_percentages_chart()
        
        if "error" in percentage_chart:
            print(f"❌ Percentage chart generation failed: {percentage_chart['error']}")
            return False
        else:
            print("✅ Outcome percentages chart generated successfully")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing chart generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting backend tests...\n")
    
    # Test data loading
    data_success = test_data_loading()
    
    if data_success:
        # Test chart generation
        chart_success = test_chart_generation()
        
        if chart_success:
            print("\n🎉 All tests passed! Backend is working correctly.")
        else:
            print("\n❌ Chart generation tests failed.")
    else:
        print("\n❌ Data loading tests failed.")

if __name__ == "__main__":
    main()
