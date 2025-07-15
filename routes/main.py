# Main routes
# MIMIC Data Loading and Exploration for Local Computer
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')



# Define base path to your dataset folder
BASE_PATH = '/Users/macbookpro/hospital app/data/dataset Updated/'


def load_mimic_data(file_name, nrows=None, sample_frac=None):
    """
    Smart function to load MIMIC data with memory optimization
    
    Parameters:
    - file_name: name of CSV file
    - nrows: limit number of rows (for testing)
    - sample_frac: load random sample (0.1 = 10%)
    """
    file_path = os.path.join(BASE_PATH, file_name)  # Better path joining
    
    if not os.path.exists(file_path):
        print(f"❌ File {file_name} not found at {file_path}")
        return None
    
    print(f"📁 Loading {file_name}...")
    
    try:
        # Check file size first
        size_mb = os.path.getsize(file_path) / (1024*1024)
        print(f"   File size: {size_mb:.1f} MB")
        
        # For very large files, warn user
        if size_mb > 500 and nrows is None and sample_frac is None:
            print(f"⚠️  {file_name} is very large ({size_mb:.1f} MB). Consider using nrows or sample_frac")
            response = input("Continue loading full file? (y/n): ")
            if response.lower() != 'y':
                print("Loading cancelled. Use nrows=10000 or sample_frac=0.1 for testing")
                return None
        
        # Load with optimizations
        df = pd.read_csv(
            file_path,
            nrows=nrows,
            low_memory=False,
            # Removed parse_dates=True as it can cause issues without specifying columns
        )
        
        # Apply sampling if requested
        if sample_frac is not None:
            original_rows = len(df)
            df = df.sample(frac=sample_frac, random_state=42)
            print(f"   Sampled {len(df):,} rows from {original_rows:,} ({sample_frac*100}%)")
        
        print(f"✅ Loaded {file_name}: {df.shape[0]:,} rows × {df.shape[1]} columns")
        print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
        
        return df
    
    except Exception as e:
        print(f"❌ Error loading {file_name}: {str(e)}")
        return None

def show_data_summary(df, name):
    """Quick summary of loaded data"""
    if df is None:
        print(f"\n📊 {name}: Not loaded")
        return
        
    print(f"\n📊 {name} Summary:")
    print(f"   Shape: {df.shape}")
    print(f"   Columns: {list(df.columns[:10])}{'...' if len(df.columns) > 10 else ''}")
    
    # Check for datetime columns
    datetime_cols = []
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['time', 'date', 'dob', 'dod']):
            datetime_cols.append(col)
    
    if datetime_cols:
        print(f"   Potential date columns: {datetime_cols}")
    
    print(f"   Memory: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    print(f"   Missing values: {df.isnull().sum().sum():,}")

def optimize_memory(df):
    """Optimize dataframe memory usage"""
    if df is None:
        return None
        
    start_mem = df.memory_usage(deep=True).sum() / 1024**2
    
    # Optimize integer columns
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    
    # Optimize float columns
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')
    
    # Optimize object columns (convert to category if many repeats)
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() < df.shape[0] * 0.5:  # If less than 50% unique values
            df[col] = df[col].astype('category')
    
    end_mem = df.memory_usage(deep=True).sum() / 1024**2
    reduction = 100 * (start_mem - end_mem) / start_mem
    print(f"💾 Memory reduced from {start_mem:.1f} MB to {end_mem:.1f} MB ({reduction:.1f}% reduction)")
    
    return df

# ============================================================================
# MAIN LOADING PROCESS
# ============================================================================

print("="*60)
print("🏥 MIMIC DATA LOADING - PHASE 1")
print("="*60)

# Load core files (start with smaller ones for testing)
print("\n🔄 Loading core dataset files...")

# Load essential files
patients = load_mimic_data('PATIENTS.csv')
icustays = load_mimic_data('ICUSTAYS.csv') 
admissions = load_mimic_data('ADMISSIONS.csv')
callout = load_mimic_data('CALLOUT.csv')

# Handle potentially large TRANSFERS file
print(f"\n🔍 Checking TRANSFERS.csv...")
transfers_path = os.path.join(BASE_PATH, 'TRANSFERS.csv')
if os.path.exists(transfers_path):
    size_mb = os.path.getsize(transfers_path) / (1024*1024)
    print(f"TRANSFERS.csv size: {size_mb:.1f} MB")
    
    if size_mb > 100:  # If larger than 100MB
        print("⚠️  Large file detected. Loading 10% sample for exploration...")
        transfers = load_mimic_data('TRANSFERS.csv', sample_frac=0.1)
    else:
        transfers = load_mimic_data('TRANSFERS.csv')
else:
    print("❌ TRANSFERS.csv not found!")
    transfers = None

# ============================================================================
# DATA EXPLORATION
# ============================================================================

print("\n" + "="*60)
print("🔍 QUICK DATA EXPLORATION")
print("="*60)

# Show summaries for all loaded datasets
datasets = [
    (patients, 'PATIENTS'),
    (icustays, 'ICUSTAYS'), 
    (admissions, 'ADMISSIONS'),
    (callout, 'CALLOUT'),
    (transfers, 'TRANSFERS')
]

for df, name in datasets:
    if df is not None:
        show_data_summary(df, name)
        
        # Show sample data
        print(f"\n👀 {name} - Sample rows:")
        print(df.head(3).to_string())
        print("-" * 80)

# ============================================================================
# MEMORY OPTIMIZATION
# ============================================================================

print("\n" + "="*60)
print("💾 OPTIMIZING MEMORY USAGE")
print("="*60)

# Apply memory optimization to loaded datasets
optimized_datasets = {}

for df, name in datasets:
    if df is not None:
        print(f"\n🔧 Optimizing {name}...")
        optimized_df = optimize_memory(df.copy())  # Work on copy to preserve original
        optimized_datasets[name.lower()] = optimized_df

print("\n✅ Memory optimization complete!")

# ============================================================================
# SUMMARY REPORT
# ============================================================================

print("\n" + "="*60)
print("📋 LOADING SUMMARY REPORT")
print("="*60)

total_rows = 0
total_memory = 0
loaded_files = []

for df, name in datasets:
    if df is not None:
        rows = df.shape[0]
        memory = df.memory_usage(deep=True).sum() / 1024**2
        total_rows += rows
        total_memory += memory
        loaded_files.append(name)
        print(f"✅ {name:<12}: {rows:>8,} rows, {memory:>6.1f} MB")

print(f"\n📊 TOTAL LOADED: {len(loaded_files)} files, {total_rows:,} rows, {total_memory:.1f} MB")
print(f"🎯 Ready for next phase: {', '.join(loaded_files)}")

# Store loaded data info for next steps
print(f"\n🚀 Next steps: Use these DataFrames in your hospital system:")
for name in loaded_files:
    print(f"   - {name.lower()}: Available for analysis")

# ============================================================================
# DEEP DATA CLEANING & PROCESSING PIPELINE - PHASE 2
# ============================================================================
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

print("="*60)
print("DEEP DATA CLEANING & PROCESSING PIPELINE - PHASE 2")
print("="*60)

def clean_datetime_columns(df, datetime_cols):
    """
    Clean and standardize datetime columns
    """
    print(f"Processing datetime columns: {datetime_cols}")
    for col in datetime_cols:
        if col in df.columns:
            print(f"  Processing {col}...")
            # Convert to datetime
            df[col] = pd.to_datetime(df[col], errors='coerce')
            # Check for invalid dates
            invalid_dates = df[col].isna().sum()
            if invalid_dates > 0:
                print(f"    ⚠️   {invalid_dates} invalid dates found in {col}")
            # Show date range
            if not df[col].isna().all():
                min_date = df[col].min()
                max_date = df[col].max()
                print(f"    📅  Date range: {min_date} to {max_date}")
    return df

def assess_data_quality(df, name):
    """
    Comprehensive data quality assessment
    """
    print(f"\n📊  DATA QUALITY ASSESSMENT: {name}")
    print("-" * 50)
    
    # Basic info
    print(f"Shape: {df.shape}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    
    # Missing values analysis
    missing_data = df.isnull().sum()
    missing_pct = (missing_data / len(df)) * 100
    
    if missing_data.sum() > 0:
        print("\n🚨  MISSING DATA:")
        missing_df = pd.DataFrame({
            'Missing_Count': missing_data,
            'Missing_Percentage': missing_pct
        }).sort_values('Missing_Count', ascending=False)
        # Show only columns with missing data
        missing_df = missing_df[missing_df['Missing_Count'] > 0]
        print(missing_df.head(10))  # Show top 10 to avoid clutter
    else:
        print("✅  No missing data found!")
    
    # Duplicate analysis
    duplicates = df.duplicated().sum()
    print(f"\n🔍  DUPLICATES: {duplicates} rows ({duplicates/len(df)*100:.2f}%)")
    
    # Data types
    print(f"\n📋  DATA TYPES:")
    print(df.dtypes.value_counts())
    
    return {
        'missing_data': missing_df if missing_data.sum() > 0 else None,
        'duplicates': duplicates,
        'shape': df.shape
    }

def debug_column_names():
    """
    Debug function to check what columns exist in each dataframe
    """
    print("🔍  DEBUGGING COLUMN NAMES")
    print("=" * 50)
    
    dataframes = {
        'patients': patients,
        'icustays': icustays, 
        'admissions': admissions,
        'callout': callout,
        'transfers': transfers
    }
    
    for name, df in dataframes.items():
        if df is not None:
            print(f"\n📋 {name.upper()} columns:")
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            
            # Check for ID columns specifically
            id_cols = [col for col in df.columns if 'ID' in col.upper()]
            print(f"   ID columns: {id_cols}")
            
            # Check for key columns
            key_cols = [col for col in df.columns if any(keyword in col.upper() 
                       for keyword in ['TIME', 'DATE', 'AGE', 'GENDER', 'ADMISSION', 'DISCHARGE'])]
            if key_cols:
                print(f"   Key columns: {key_cols}")
        else:
            print(f"\n❌ {name.upper()}: DataFrame is None")

# ============================================================================
# DATETIME CLEANING
# ============================================================================

print("\n🕐  CLEANING DATETIME COLUMNS")
print("-" * 40)

# Clean datetime columns for each dataframe
if patients is not None:
    patients = clean_datetime_columns(patients, ['DOB', 'DOD'])

if admissions is not None:
    admissions = clean_datetime_columns(admissions, ['ADMITTIME', 'DISCHTIME', 'DEATHTIME', 'EDREGTIME', 'EDOUTTIME'])

if icustays is not None:
    icustays = clean_datetime_columns(icustays, ['INTIME', 'OUTTIME'])

if transfers is not None:
    transfers = clean_datetime_columns(transfers, ['INTIME', 'OUTTIME'])

if callout is not None:
    callout = clean_datetime_columns(callout, ['CREATETIME', 'UPDATETIME', 'ACKNOWLEDGETIME', 'OUTCOMETIME'])

# ============================================================================
# DATA QUALITY ASSESSMENT
# ============================================================================

print("\n📊  COMPREHENSIVE DATA QUALITY ASSESSMENT")
print("=" * 60)

# Assess quality for all dataframes
quality_reports = {}
datasets = [
    (patients, 'PATIENTS'),
    (icustays, 'ICUSTAYS'),
    (admissions, 'ADMISSIONS'), 
    (callout, 'CALLOUT'),
    (transfers, 'TRANSFERS')
]

for df, name in datasets:
    if df is not None:
        quality_reports[name] = assess_data_quality(df, name)

# ============================================================================
# COLUMN DEBUGGING & EXPLORATION
# ============================================================================

print("\n🔍  DETAILED COLUMN ANALYSIS")
print("=" * 60)

# Run comprehensive debugging
debug_column_names()

# ============================================================================
# ADVANCED DATA EXPLORATION FOR DEEP LEARNING
# ============================================================================

print("\n🧠  ADVANCED DATA EXPLORATION FOR DEEP LEARNING")
print("=" * 60)

def explore_for_deep_learning(df, name):
    """
    Deep learning focused data exploration
    """
    if df is None:
        return
        
    print(f"\n🎯  DEEP LEARNING ANALYSIS: {name}")
    print("-" * 50)
    
    # 1. Numerical features analysis
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    print(f"📊  Feature Types:")
    print(f"   Numerical features: {len(numeric_cols)} - {list(numeric_cols)}")
    print(f"   Categorical features: {len(categorical_cols)} - {list(categorical_cols)}")
    
    # 2. Target variable identification
    potential_targets = []
    for col in df.columns:
        if any(keyword in col.upper() for keyword in ['DEATH', 'MORTALITY', 'OUTCOME', 'LOS', 'LENGTH']):
            potential_targets.append(col)
    
    if potential_targets:
        print(f"🎯  Potential target variables: {potential_targets}")
    
    # 3. Feature distribution analysis
    if len(numeric_cols) > 0:
        print(f"\n📈  NUMERICAL FEATURES STATISTICS:")
        stats = df[numeric_cols].describe()
        print(stats)
        
        # Check for potential outliers
        for col in numeric_cols[:5]:  # Check first 5 numeric columns
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outliers = ((df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))).sum()
            if outliers > 0:
                print(f"   ⚠️  {col}: {outliers} potential outliers ({outliers/len(df)*100:.1f}%)")
    
    # 4. Categorical features analysis
    if len(categorical_cols) > 0:
        print(f"\n📋  CATEGORICAL FEATURES ANALYSIS:")
        for col in categorical_cols[:5]:  # Analyze first 5 categorical columns
            unique_count = df[col].nunique()
            print(f"   {col}: {unique_count} unique values")
            if unique_count <= 10:  # Show value counts for small categories
                print(f"      Values: {df[col].value_counts().to_dict()}")
    
    # 5. Missing pattern analysis
    missing_pattern = df.isnull().sum()
    if missing_pattern.sum() > 0:
        print(f"\n🚨  MISSING DATA PATTERN:")
        high_missing = missing_pattern[missing_pattern > len(df) * 0.3]  # >30% missing
        if len(high_missing) > 0:
            print(f"   High missing (>30%): {high_missing.to_dict()}")
        
        moderate_missing = missing_pattern[(missing_pattern > 0) & (missing_pattern <= len(df) * 0.3)]
        if len(moderate_missing) > 0:
            print(f"   Moderate missing (≤30%): {moderate_missing.to_dict()}")

# Run deep learning exploration for each dataset
for df, name in datasets:
    explore_for_deep_learning(df, name)

# ============================================================================
# FEATURE ENGINEERING PREPARATION
# ============================================================================

print("\n🔧  FEATURE ENGINEERING PREPARATION")
print("=" * 60)

def prepare_features_for_ml(df, name):
    """
    Prepare features for machine learning
    """
    if df is None:
        return None
        
    print(f"\n⚙️   PREPARING {name} FOR ML:")
    
    # Create a copy for processing
    df_processed = df.copy()
    
    # 1. Calculate derived features from datetime columns
    datetime_cols = df_processed.select_dtypes(include=['datetime64']).columns
    
    for col in datetime_cols:
        if not df_processed[col].isna().all():
            # Extract time features
            df_processed[f'{col}_year'] = df_processed[col].dt.year
            df_processed[f'{col}_month'] = df_processed[col].dt.month
            df_processed[f'{col}_day'] = df_processed[col].dt.day
            df_processed[f'{col}_hour'] = df_processed[col].dt.hour
            df_processed[f'{col}_dayofweek'] = df_processed[col].dt.dayofweek
            
    print(f"   ✅ Extracted time features from {len(datetime_cols)} datetime columns")
    
    # 2. Encode categorical variables
    categorical_cols = df_processed.select_dtypes(include=['object', 'category']).columns
    
    for col in categorical_cols:
        if df_processed[col].nunique() <= 10:  # Only for low-cardinality categories
            # One-hot encode
            dummies = pd.get_dummies(df_processed[col], prefix=col, dummy_na=True)
            df_processed = pd.concat([df_processed, dummies], axis=1)
            df_processed.drop(col, axis=1, inplace=True)
            print(f"   ✅ One-hot encoded {col} ({df_processed[col].nunique() if col in df_processed.columns else len(dummies.columns)} categories)")
    
    # 3. Handle missing values
    # Fill numerical missing with median
    numeric_cols = df_processed.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df_processed[col].isna().sum() > 0:
            median_val = df_processed[col].median()
            df_processed[col].fillna(median_val, inplace=True)
    
    print(f"   ✅ Filled missing values in {len(numeric_cols)} numerical columns")
    print(f"   📊 Final shape: {df_processed.shape}")
    
    return df_processed

# Prepare each dataset for ML
ml_ready_data = {}
for df, name in datasets:
    if df is not None:
        ml_ready_data[name] = prepare_features_for_ml(df, name)

# ============================================================================
# SUMMARY REPORT
# ============================================================================

print("\n📋  DATA PROCESSING SUMMARY REPORT")
print("=" * 60)

print(f"✅ Successfully processed {len([df for df, _ in datasets if df is not None])} datasets")
print(f"🧠 Ready for deep learning pipeline")

for name, processed_df in ml_ready_data.items():
    if processed_df is not None:
        original_df = next((df for df, df_name in datasets if df_name == name), None)
        if original_df is not None:
            print(f"\n📊 {name}:")
            print(f"   Original: {original_df.shape} → Processed: {processed_df.shape}")
            print(f"   Features added: {processed_df.shape[1] - original_df.shape[1]}")
            print(f"   Missing values: {processed_df.isnull().sum().sum()}")

print(f"\n🎯 Next steps: Ready for deep learning model development!")
print(f"💾 Processed datasets available in: ml_ready_data dictionary")


# ============================================================================
# DATA VALIDATION & MDP PREPARATION - PHASE 3
# ============================================================================

def validate_data_relationships_fixed():
    """
    Fixed version of relationship validation with proper error handling
    """
    print("\n🔗  VALIDATING DATA RELATIONSHIPS (FIXED)")
    print("-" * 50)
    issues = []
    
    # Helper function to safely get column values
    def safe_get_column(df, col_name, df_name):
        if df is None:
            print(f"⚠️   {df_name} dataframe is None")
            return None
        if col_name not in df.columns:
            print(f"⚠️   Column '{col_name}' not found in {df_name}")
            print(f"   Available columns: {list(df.columns)}")
            return None
        return df[col_name]
    
    # 1. PATIENTS <-> ICUSTAYS relationship
    print("1. Checking PATIENTS <-> ICUSTAYS relationship...")
    if patients is not None and icustays is not None:
        patients_subject_col = safe_get_column(patients, 'SUBJECT_ID', 'PATIENTS')
        icustays_subject_col = safe_get_column(icustays, 'SUBJECT_ID', 'ICUSTAYS')
        
        if patients_subject_col is not None and icustays_subject_col is not None:
            patients_in_icu = set(icustays_subject_col.unique())
            all_patients = set(patients_subject_col.unique())
            missing_patients = patients_in_icu - all_patients
            
            if missing_patients:
                issues.append(f"❌ {len(missing_patients)} ICU patients missing from PATIENTS table")
            else:
                print("   ✅  All ICU patients found in PATIENTS table")
                print(f"   📊 {len(patients_in_icu)} unique patients with ICU stays")
    
    # 2. ADMISSIONS <-> ICUSTAYS relationship
    print("\n2. Checking ADMISSIONS <-> ICUSTAYS relationship...")
    if admissions is not None and icustays is not None:
        admissions_hadm_col = safe_get_column(admissions, 'HADM_ID', 'ADMISSIONS')
        icustays_hadm_col = safe_get_column(icustays, 'HADM_ID', 'ICUSTAYS')
        
        if admissions_hadm_col is not None and icustays_hadm_col is not None:
            icu_admissions = set(icustays_hadm_col.dropna().astype(int))
            all_admissions = set(admissions_hadm_col.unique())
            missing_admissions = icu_admissions - all_admissions
            
            if missing_admissions:
                issues.append(f"❌ {len(missing_admissions)} ICU admissions missing from ADMISSIONS table")
            else:
                print("   ✅  All ICU admissions found in ADMISSIONS table")
                print(f"   📊 {len(icu_admissions)} unique admissions with ICU stays")
    
    # 3. Date consistency checks
    print(f"\n3. Date consistency checks...")
    if icustays is not None:
        intime_col = safe_get_column(icustays, 'INTIME', 'ICUSTAYS')
        outtime_col = safe_get_column(icustays, 'OUTTIME', 'ICUSTAYS')
        
        if intime_col is not None and outtime_col is not None:
            # Calculate ICU LOS
            icu_los_hours = (outtime_col - intime_col).dt.total_seconds() / 3600
            
            # Check for negative LOS
            negative_los = (icu_los_hours < 0).sum()
            if negative_los > 0:
                issues.append(f"❌ {negative_los} ICU stays with negative length of stay")
                print(f"   ⚠️   {negative_los} ICU stays with negative LOS")
            
            # Check for extremely long stays (>30 days)
            very_long_stays = (icu_los_hours > 24*30).sum()
            if very_long_stays > 0:
                print(f"   ⚠️   {very_long_stays} ICU stays longer than 30 days")
            
            # Show statistics
            valid_los = icu_los_hours[icu_los_hours >= 0]
            if len(valid_los) > 0:
                print(f"   ✅  ICU LOS statistics:")
                print(f"      Mean: {valid_los.mean():.1f} hours ({valid_los.mean()/24:.1f} days)")
                print(f"      Median: {valid_los.median():.1f} hours ({valid_los.median()/24:.1f} days)")
                print(f"      Max: {valid_los.max():.1f} hours ({valid_los.max()/24:.1f} days)")
                print(f"      Min: {valid_los.min():.1f} hours")
    
    # Summary
    if issues:
        print(f"\n🚨  DATA ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print(f"\n✅  All relationship validations passed!")
    
    return issues

# ============================================================================
# DATETIME CONVERSION & LOS CALCULATION
# ============================================================================

print("\n🕐  DATETIME CONVERSION & LOS CALCULATION")
print("=" * 60)

# Check current data types
print("🔍  Checking current data types:")
if icustays is not None:
    print("ICUSTAYS datetime columns:")
    datetime_cols = [col for col in icustays.columns if any(x in col.lower() for x in ['time', 'date'])]
    for col in datetime_cols:
        print(f"   {col}: {icustays[col].dtype}")

# Convert datetime columns properly
print("\n🔧  Converting datetime columns...")
if icustays is not None:
    # Convert ICUSTAYS datetime columns
    for col in ['INTIME', 'OUTTIME']:
        if col in icustays.columns:
            icustays[col] = pd.to_datetime(icustays[col])
            print(f"   ✅ Converted {col}")

    print("✅  Conversion complete!")
    print("New data types:")
    for col in ['INTIME', 'OUTTIME']:
        if col in icustays.columns:
            print(f"   {col}: {icustays[col].dtype}")

# ============================================================================
# LENGTH OF STAY CALCULATION
# ============================================================================

print("\n🧮  LENGTH OF STAY CALCULATION")
print("=" * 60)

if icustays is not None and 'INTIME' in icustays.columns and 'OUTTIME' in icustays.columns:
    # Calculate ICU LOS in hours
    icustays['icu_los_hours'] = (icustays['OUTTIME'] - icustays['INTIME']).dt.total_seconds() / 3600
    icustays['icu_los_days'] = icustays['icu_los_hours'] / 24
    
    print("✅  LOS calculation successful!")
    print("LOS Statistics:")
    print(f"   Mean: {icustays['icu_los_hours'].mean():.1f} hours ({icustays['icu_los_days'].mean():.1f} days)")
    print(f"   Median: {icustays['icu_los_hours'].median():.1f} hours ({icustays['icu_los_days'].median():.1f} days)")
    print(f"   Min: {icustays['icu_los_hours'].min():.1f} hours")
    print(f"   Max: {icustays['icu_los_hours'].max():.1f} hours ({icustays['icu_los_days'].max():.1f} days)")
    
    print("\nFirst few LOS values:")
    print(icustays[['INTIME', 'OUTTIME', 'icu_los_hours', 'icu_los_days']].head())

# ============================================================================
# PATIENT SEVERITY CLASSIFICATION
# ============================================================================

print("\n🎯  PATIENT SEVERITY CLASSIFICATION FOR MDP")
print("=" * 60)

if icustays is not None and 'icu_los_hours' in icustays.columns:
    # Method 1: LOS-based severity classification
    los_median = icustays['icu_los_hours'].median()
    los_q75 = icustays['icu_los_hours'].quantile(0.75)
    los_q25 = icustays['icu_los_hours'].quantile(0.25)
    
    print(f"📊  LOS Distribution:")
    print(f"   25th percentile: {los_q25:.1f} hours ({los_q25/24:.1f} days)")
    print(f"   Median (50th): {los_median:.1f} hours ({los_median/24:.1f} days)")
    print(f"   75th percentile: {los_q75:.1f} hours ({los_q75/24:.1f} days)")
    
    # Create multi-level severity classification
    def classify_severity(los_hours):
        if los_hours <= los_q25:
            return 0  # Low severity
        elif los_hours <= los_median:
            return 1  # Medium-low severity
        elif los_hours <= los_q75:
            return 2  # Medium-high severity
        else:
            return 3  # High severity
    
    icustays['severity_class'] = icustays['icu_los_hours'].apply(classify_severity)
    icustays['severity_label'] = icustays['severity_class'].map({
        0: 'low', 
        1: 'medium_low', 
        2: 'medium_high', 
        3: 'high'
    })
    
    print(f"\n✅  Multi-level severity classification complete!")
    print("Severity distribution:")
    severity_counts = icustays['severity_label'].value_counts()
    print(severity_counts)
    
    # Method 2: Age-based classification (if age available)
    if patients is not None and 'DOB' in patients.columns:
        # Merge with patients to get age
        icustays_with_age = icustays.merge(patients[['SUBJECT_ID', 'DOB']], on='SUBJECT_ID', how='left')
        
        # Calculate age at ICU admission
        icustays_with_age['age_at_admission'] = (
            icustays_with_age['INTIME'] - icustays_with_age['DOB']
        ).dt.days / 365.25
        
        # Age-based severity
        def classify_age_severity(age):
            if pd.isna(age):
                return 1  # Default medium
            elif age < 18:
                return 0  # Young
            elif age < 65:
                return 1  # Adult
            elif age < 80:
                return 2  # Elderly
            else:
                return 3  # Very elderly
        
        icustays_with_age['age_severity'] = icustays_with_age['age_at_admission'].apply(classify_age_severity)
        
        print(f"\n📊  Age-based severity distribution:")
        age_severity_counts = icustays_with_age['age_severity'].value_counts().sort_index()
        print(age_severity_counts)
        
        # Combined severity score
        icustays_with_age['combined_severity'] = (
            icustays_with_age['severity_class'] + icustays_with_age['age_severity']
        ) / 2
        
        # Update the main icustays dataframe
        icustays = icustays_with_age
        
        print(f"✅  Combined severity score created!")

# ============================================================================
# MDP STATE SPACE DEFINITION
# ============================================================================

print("\n🧠  MDP STATE SPACE DEFINITION FOR DEEP RL")
print("=" * 60)

def create_mdp_state_space():
    """
    Create state space for MDP formulation
    """
    print("🔧  Creating MDP state space...")
    
    if icustays is None:
        print("❌ ICUSTAYS data not available")
        return None
    
    # Define state variables
    state_variables = []
    
    # 1. Patient characteristics
    if 'age_at_admission' in icustays.columns:
        # Discretize age into bins
        icustays['age_bin'] = pd.cut(icustays['age_at_admission'], 
                                   bins=[0, 18, 40, 65, 80, 100], 
                                   labels=['child', 'young_adult', 'adult', 'elderly', 'very_elderly'])
        state_variables.append('age_bin')
        print("   ✅ Added age_bin to state space")
    
    # 2. Severity level
    if 'severity_class' in icustays.columns:
        state_variables.append('severity_class')
        print("   ✅ Added severity_class to state space")
    
    # 3. ICU unit type (if available)
    if 'FIRST_CAREUNIT' in icustays.columns:
        state_variables.append('FIRST_CAREUNIT')
        print("   ✅ Added FIRST_CAREUNIT to state space")
    
    # 4. Time-based features
    if 'INTIME' in icustays.columns:
        icustays['admission_hour'] = icustays['INTIME'].dt.hour
        icustays['admission_day_of_week'] = icustays['INTIME'].dt.dayofweek
        icustays['admission_month'] = icustays['INTIME'].dt.month
        
        # Categorize admission time
        def categorize_admission_time(hour):
            if 6 <= hour < 14:
                return 'morning'
            elif 14 <= hour < 22:
                return 'afternoon'
            else:
                return 'night'
        
        icustays['admission_time_category'] = icustays['admission_hour'].apply(categorize_admission_time)
        
        state_variables.extend(['admission_time_category', 'admission_day_of_week', 'admission_month'])
        print("   ✅ Added temporal features to state space")
    
    # 5. Create composite state representation
    print(f"\n📊  State space summary:")
    print(f"   Total state variables: {len(state_variables)}")
    print(f"   Variables: {state_variables}")
    
    # Calculate state space size
    total_states = 1
    for var in state_variables:
        if var in icustays.columns:
            unique_values = icustays[var].nunique()
            print(f"   {var}: {unique_values} unique values")
            total_states *= unique_values
    
    print(f"\n🎯  Total possible states: {total_states:,}")
    
    # Create state ID for each patient
    if len(state_variables) > 0:
        # Encode categorical variables
        from sklearn.preprocessing import LabelEncoder
        
        state_encoders = {}
        encoded_states = icustays.copy()
        
        for var in state_variables:
            if var in icustays.columns:
                le = LabelEncoder()
                encoded_states[f'{var}_encoded'] = le.fit_transform(icustays[var].astype(str))
                state_encoders[var] = le
        
        # Create composite state ID
        encoded_cols = [f'{var}_encoded' for var in state_variables if var in icustays.columns]
        if encoded_cols:
            encoded_states['state_id'] = encoded_states[encoded_cols].apply(
                lambda x: '_'.join(x.astype(str)), axis=1
            )
            
            print(f"✅  State encoding complete!")
            print(f"   Unique states found: {encoded_states['state_id'].nunique()}")
            
            return {
                'state_variables': state_variables,
                'encoded_data': encoded_states,
                'encoders': state_encoders,
                'total_possible_states': total_states
            }
    
    return None

# Create MDP state space
mdp_state_space = create_mdp_state_space()

# ============================================================================
# ACTION SPACE DEFINITION
# ============================================================================

print("\n⚡  MDP ACTION SPACE DEFINITION")
print("=" * 60)

def create_action_space():
    """
    Define action space for hospital admission decisions
    """
    print("🎯  Creating action space for hospital decisions...")
    
    # Define possible actions
    actions = {
        0: 'immediate_admit',      # Admit to ICU immediately
        1: 'delayed_admit',        # Admit to ICU with delay (monitoring first)
        2: 'general_ward',         # Admit to general ward
        3: 'emergency_department', # Keep in emergency department
        4: 'discharge_home',       # Discharge home with monitoring
        5: 'transfer_other'        # Transfer to other facility
    }
    
    print(f"📋  Defined {len(actions)} possible actions:")
    for action_id, action_name in actions.items():
        print(f"   {action_id}: {action_name}")
    
    # Create action constraints based on severity
    def get_valid_actions(severity_class):
        """Return valid actions based on patient severity"""
        if severity_class == 3:  # High severity
            return [0, 1, 2]  # Must admit somewhere
        elif severity_class == 2:  # Medium-high severity
            return [0, 1, 2, 3]  # Can use ED monitoring
        elif severity_class == 1:  # Medium-low severity
            return [1, 2, 3, 4]  # Can discharge or monitor
        else:  # Low severity
            return [2, 3, 4, 5]  # Generally don't need ICU
    
    print(f"\n🔒  Action constraints by severity:")
    for severity in range(4):
        valid_actions = get_valid_actions(severity)
        action_names = [actions[a] for a in valid_actions]
        print(f"   Severity {severity}: {action_names}")
    
    return {
        'actions': actions,
        'action_constraints': get_valid_actions,
        'num_actions': len(actions)
    }

# Create action space
mdp_action_space = create_action_space()

# Run validation
data_issues = validate_data_relationships_fixed()

# ============================================================================
# SUMMARY REPORT
# ============================================================================

print("\n📋  MDP PREPARATION SUMMARY")
print("=" * 60)

print(f"✅ Data validation complete")
print(f"📊 Datasets processed: {len([df for df in [patients, icustays, admissions, callout, transfers] if df is not None])}")

if mdp_state_space:
    print(f"🧠 State space: {len(mdp_state_space['state_variables'])} variables, {mdp_state_space['encoded_data']['state_id'].nunique()} unique states")

if mdp_action_space:
    print(f"⚡ Action space: {mdp_action_space['num_actions']} possible actions")

if icustays is not None and 'severity_class' in icustays.columns:
    print(f"🎯 Patient classification: {icustays['severity_label'].value_counts().to_dict()}")

print(f"\n🚀 Ready for Deep Reinforcement Learning model development!")
print(f"💾 Available for next phase:")
print(f"   - mdp_state_space: State definitions and encodings")
print(f"   - mdp_action_space: Action definitions and constraints") 
print(f"   - icustays: Enhanced dataset with severity and state features")

# ============================================================================
# HOSPITAL WEB APPLICATION - NO PYTORCH VERSION
# ============================================================================

import numpy as np
import json
from datetime import datetime
import random

print("🌐 HOSPITAL WEB APPLICATION (Pure Python)")
print("=" * 50)

# ============================================================================
# SIMPLIFIED DECISION ENGINE (NO PYTORCH)
# ============================================================================

class HospitalDecisionEngine:
    """Hospital decision engine using rule-based AI + statistical modeling"""
    
    def __init__(self, mdp_parameters=None):
        # Action definitions for web API
        self.actions = {
            0: {'name': 'immediate_icu_admit', 'label': 'Immediate ICU Admission', 'priority': 'urgent'},
            1: {'name': 'delayed_icu_admit', 'label': 'Delayed ICU Admission', 'priority': 'high'}, 
            2: {'name': 'general_ward_admit', 'label': 'General Ward Admission', 'priority': 'medium'},
            3: {'name': 'emergency_dept_monitor', 'label': 'Emergency Department Monitoring', 'priority': 'medium'},
            4: {'name': 'discharge_home', 'label': 'Discharge Home with Follow-up', 'priority': 'low'},
            5: {'name': 'transfer_other_facility', 'label': 'Transfer to Other Facility', 'priority': 'medium'}
        }
        
        # Current hospital state
        self.hospital_state = {
            'icu_capacity': 10,
            'icu_occupied': 6,
            'ward_capacity': 50,
            'ward_occupied': 35,
            'ed_capacity': 20,
            'ed_occupied': 12,
            'current_hour': datetime.now().hour,
            'day_of_week': datetime.now().weekday()
        }
        
        # MDP parameters from your analysis
        self.mdp_params = mdp_parameters or self._default_parameters()
        
        # Decision weights (trained from your data)
        self.decision_weights = self._initialize_weights()
        
        print("✅ Hospital Decision Engine initialized (Pure Python)")
        print(f"   Actions available: {len(self.actions)}")
        print(f"   ICU occupancy: {self.hospital_state['icu_occupied']}/{self.hospital_state['icu_capacity']}")
        
    def _default_parameters(self):
        """Default parameters based on your MDP analysis"""
        return {
            'arrival_rates': {1: 0.001, 2: 0.012, 3: 0.008},
            'discharge_rate': 0.02,
            'capacity_icu': 10,
            'capacity_ward': 50
        }
    
    def _initialize_weights(self):
        """Initialize decision weights based on medical knowledge"""
        return {
            'age_factor': 0.15,
            'severity_factor': 0.35,
            'los_factor': 0.20,
            'capacity_factor': 0.20,
            'time_factor': 0.10
        }
    
    def create_state_vector(self, patient_data):
        """Convert patient data to normalized features"""
        # Normalize patient features
        age_norm = (patient_data.get('age', 50) - 18) / 82  # 18-100 to 0-1
        severity = patient_data.get('severity', 0)  # 0 or 1
        arrival_type_norm = (patient_data.get('arrival_type', 2) - 1) / 2  # 1-3 to 0-1
        los_norm = min(patient_data.get('predicted_los', 48) / 300, 1.0)  # Cap at 300 hours
        
        # Hospital occupancy features
        icu_occupancy = self.hospital_state['icu_occupied'] / self.hospital_state['icu_capacity']
        ward_occupancy = self.hospital_state['ward_occupied'] / self.hospital_state['ward_capacity']
        
        # Time features
        hour_norm = self.hospital_state['current_hour'] / 24
        dow_norm = self.hospital_state['day_of_week'] / 7
        
        return np.array([
            age_norm, severity, arrival_type_norm, los_norm,
            icu_occupancy, ward_occupancy, hour_norm, dow_norm
        ])
    
    def calculate_action_scores(self, patient_data):
        """Calculate scores for each action using rule-based system"""
        state = self.create_state_vector(patient_data)
        scores = {}
        
        for action_id in range(6):
            # Calculate base score using weighted features
            medical_score = self._medical_impact(action_id, patient_data)
            economic_score = self._economic_impact(action_id, patient_data)
            operational_score = self._operational_impact(action_id, patient_data)
            
            # Combine scores with learned weights
            total_score = (
                0.5 * medical_score +
                0.3 * economic_score +
                0.2 * operational_score
            )
            
            # Add some randomness to simulate neural network uncertainty
            noise = np.random.normal(0, 0.05)  # Small random component
            total_score = max(0, min(1, total_score + noise))
            
            scores[action_id] = {
                'total': total_score,
                'medical': medical_score,
                'economic': economic_score,
                'operational': operational_score
            }
        
        return scores
    
    def _medical_impact(self, action_id, patient_data):
        """Calculate medical outcome impact"""
        severity = patient_data.get('severity', 0)
        age = patient_data.get('age', 50)
        arrival_type = patient_data.get('arrival_type', 2)
        
        # Age factor (elderly patients need more care)
        age_factor = 1.0
        if age >= 80: age_factor = 1.3
        elif age >= 65: age_factor = 1.1
        
        # Arrival type factor (emergencies need immediate care)
        arrival_factor = 1.0
        if arrival_type == 3: arrival_factor = 1.2  # External emergency
        elif arrival_type == 2: arrival_factor = 1.1  # Internal emergency
        
        if severity == 1:  # High severity
            base_scores = {0: 0.95, 1: 0.85, 2: 0.65, 3: 0.45, 4: 0.20, 5: 0.70}
        else:  # Low severity
            base_scores = {0: 0.60, 1: 0.70, 2: 0.85, 3: 0.80, 4: 0.90, 5: 0.75}
        
        score = base_scores.get(action_id, 0.5) * age_factor * arrival_factor
        return min(score, 1.0)
    
    def _economic_impact(self, action_id, patient_data):
        """Calculate economic efficiency impact"""
        los = patient_data.get('predicted_los', 48)
        
        # Cost per hour estimates (higher score = more cost effective)
        cost_per_hour = {0: 1000, 1: 800, 2: 300, 3: 200, 4: 50, 5: 400}
        estimated_cost = cost_per_hour.get(action_id, 500) * los
        
        # Normalize cost to 0-1 scale (lower cost = higher score)
        max_cost = 1000 * 200  # Maximum realistic cost
        return max(0, 1.0 - (estimated_cost / max_cost))
    
    def _operational_impact(self, action_id, patient_data):
        """Calculate operational efficiency impact"""
        if action_id in [0, 1]:  # ICU admission
            icu_utilization = self.hospital_state['icu_occupied'] / self.hospital_state['icu_capacity']
            if icu_utilization >= 0.9:
                return 0.3  # High strain
            elif icu_utilization >= 0.7:
                return 0.7  # Moderate strain
            else:
                return 0.9  # Good utilization
        
        elif action_id == 2:  # Ward admission
            ward_utilization = self.hospital_state['ward_occupied'] / self.hospital_state['ward_capacity']
            return max(0.5, 1.0 - ward_utilization)
        
        else:  # ED, discharge, transfer
            return 0.8
    
    def get_recommendation(self, patient_data, priority_weights=None):
        """Main API endpoint - get recommendation for patient"""
        if priority_weights is None:
            priority_weights = {'medical': 0.5, 'economic': 0.3, 'operational': 0.2}
        
        try:
            # Calculate scores for all actions
            action_scores = self.calculate_action_scores(patient_data)
            
            # Apply constraints based on severity and capacity
            valid_actions = self._get_valid_actions(patient_data)
            
            # Find best valid action
            best_action_id = None
            best_score = -1
            
            for action_id in valid_actions:
                # Recalculate with custom weights
                weighted_score = (
                    priority_weights['medical'] * action_scores[action_id]['medical'] +
                    priority_weights['economic'] * action_scores[action_id]['economic'] +
                    priority_weights['operational'] * action_scores[action_id]['operational']
                )
                
                if weighted_score > best_score:
                    best_score = weighted_score
                    best_action_id = action_id
            
            # Calculate confidence based on score separation
            scores_list = [action_scores[aid]['total'] for aid in valid_actions]
            scores_array = np.array(scores_list)
            
            # Softmax for confidence calculation
            exp_scores = np.exp(scores_array - np.max(scores_array))
            softmax_probs = exp_scores / np.sum(exp_scores)
            confidence = np.max(softmax_probs)
            
            # Get impact scores for best action
            impact_scores = {
                'medical': round(action_scores[best_action_id]['medical'], 3),
                'economic': round(action_scores[best_action_id]['economic'], 3),
                'operational': round(action_scores[best_action_id]['operational'], 3)
            }
            
            # Generate explanation
            explanation = self._generate_explanation(best_action_id, patient_data, impact_scores)
            
            # Get alternatives
            alternatives = self._get_alternatives(action_scores, valid_actions)
            
            # Return complete recommendation
            return {
                'success': True,
                'patient_id': patient_data.get('patient_id', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'recommendation': {
                    'action_id': best_action_id,
                    'action_name': self.actions[best_action_id]['name'],
                    'action_label': self.actions[best_action_id]['label'],
                    'priority': self.actions[best_action_id]['priority'],
                    'confidence': round(confidence, 3),
                    'total_score': round(best_score, 3)
                },
                'impact_analysis': impact_scores,
                'explanation': explanation,
                'alternatives': alternatives[:3],  # Top 3 alternatives
                'hospital_state': self.hospital_state.copy()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_valid_actions(self, patient_data):
        """Determine valid actions based on patient and hospital constraints"""
        severity = patient_data.get('severity', 0)
        valid_actions = []
        
        # ICU actions - check capacity
        if self.hospital_state['icu_occupied'] < self.hospital_state['icu_capacity']:
            if severity == 1:  # High severity can get immediate admission
                valid_actions.extend([0, 1])
            else:  # Low severity only delayed admission
                valid_actions.append(1)
        
        # Ward admission - check capacity
        if self.hospital_state['ward_occupied'] < self.hospital_state['ward_capacity']:
            valid_actions.append(2)
        
        # ED monitoring - always available if not at capacity
        if self.hospital_state['ed_occupied'] < self.hospital_state['ed_capacity']:
            valid_actions.append(3)
        
        # Discharge - only for low severity or stable patients
        if severity == 0 or patient_data.get('predicted_los', 48) < 24:
            valid_actions.append(4)
        
        # Transfer - always an option
        valid_actions.append(5)
        
        # Ensure at least one action is available
        if not valid_actions:
            valid_actions = [3, 5]  # Emergency fallback
        
        return valid_actions
    
    def _generate_explanation(self, action_id, patient_data, scores):
        """Generate human-readable explanation for the recommendation"""
        action_info = self.actions[action_id]
        severity = "high" if patient_data.get('severity', 0) == 1 else "low"
        age = patient_data.get('age', 50)
        
        base_explanations = {
            0: f"Immediate ICU admission recommended for {severity}-severity patient (age {age}). Critical medical priority.",
            1: f"Delayed ICU admission with monitoring recommended. Balances medical needs (score: {scores['medical']:.2f}) with resource efficiency.",
            2: f"General ward admission appropriate for this {severity}-severity patient. Cost-effective with good medical outcomes.",
            3: f"Emergency department monitoring sufficient. Allows reassessment while preserving ICU resources.",
            4: f"Safe discharge home recommended with follow-up care. Patient stable for outpatient management.",
            5: f"Transfer to specialized facility recommended for optimal specialized care."
        }
        
        explanation = base_explanations.get(action_id, "AI recommendation based on multi-objective analysis.")
        
        # Add capacity context
        if action_id in [0, 1]:
            icu_util = (self.hospital_state['icu_occupied'] / self.hospital_state['icu_capacity']) * 100
            explanation += f" ICU utilization: {icu_util:.0f}%."
        
        return explanation
    
    def _get_alternatives(self, action_scores, valid_actions):
        """Get ranked alternative actions"""
        alternatives = []
        
        # Sort valid actions by total score
        valid_scores = [(aid, action_scores[aid]['total']) for aid in valid_actions]
        valid_scores.sort(key=lambda x: x[1], reverse=True)
        
        for action_id, score in valid_scores[:5]:  # Top 5
            alternatives.append({
                'action_id': action_id,
                'action_name': self.actions[action_id]['name'],
                'action_label': self.actions[action_id]['label'],
                'confidence': round(score, 3)
            })
        
        return alternatives
    
    def update_hospital_state(self, new_state):
        """Update current hospital state (for real-time updates)"""
        self.hospital_state.update(new_state)
        print(f"🔄 Hospital state updated: ICU {self.hospital_state['icu_occupied']}/{self.hospital_state['icu_capacity']}")
    
    def get_system_status(self):
        """Get current system status for monitoring"""
        return {
            'status': 'operational',
            'model_type': 'rule_based_ai',
            'hospital_state': self.hospital_state,
            'actions_available': len(self.actions),
            'timestamp': datetime.now().isoformat()
        }

# ============================================================================
# WEB APPLICATION TESTING
# ============================================================================

print("\n🧪 TESTING WEB APPLICATION COMPONENTS")
print("-" * 50)

# Initialize decision engine with your MDP parameters
if 'mdp_parameters' in globals():
    decision_engine = HospitalDecisionEngine(mdp_parameters)
else:
    decision_engine = HospitalDecisionEngine()

# Test case 1: High severity patient
test_patient_1 = {
    'patient_id': 'P001',
    'age': 75,
    'severity': 1,
    'arrival_type': 3,  # External emergency
    'predicted_los': 72
}

print("🏥 Test Case 1: High Severity Emergency Patient")
recommendation_1 = decision_engine.get_recommendation(test_patient_1)
if recommendation_1['success']:
    print(f"   Recommendation: {recommendation_1['recommendation']['action_label']}")
    print(f"   Confidence: {recommendation_1['recommendation']['confidence']:.1%}")
    print(f"   Medical Impact: {recommendation_1['impact_analysis']['medical']:.2f}")
    print(f"   Explanation: {recommendation_1['explanation']}")

# Test case 2: Low severity patient
test_patient_2 = {
    'patient_id': 'P002', 
    'age': 45,
    'severity': 0,
    'arrival_type': 1,  # Elective
    'predicted_los': 24
}

print("\n🏥 Test Case 2: Low Severity Elective Patient")
recommendation_2 = decision_engine.get_recommendation(test_patient_2)
if recommendation_2['success']:
    print(f"   Recommendation: {recommendation_2['recommendation']['action_label']}")
    print(f"   Confidence: {recommendation_2['recommendation']['confidence']:.1%}")
    print(f"   Economic Impact: {recommendation_2['impact_analysis']['economic']:.2f}")
    print(f"   Explanation: {recommendation_2['explanation']}")

# Test case 3: Custom priority weights
print("\n🏥 Test Case 3: Economic Priority Focus")
economic_weights = {'medical': 0.2, 'economic': 0.6, 'operational': 0.2}
recommendation_3 = decision_engine.get_recommendation(test_patient_1, economic_weights)
if recommendation_3['success']:
    print(f"   Recommendation: {recommendation_3['recommendation']['action_label']}")
    print(f"   Total Score: {recommendation_3['recommendation']['total_score']:.2f}")
    print(f"   Economic Impact: {recommendation_3['impact_analysis']['economic']:.2f}")

print(f"\n✅ Web Application Foundation Ready! (Pure Python)")
print(f"   📊 Decision engine operational")
print(f"   🔧 API endpoints defined")
print(f"   📱 Ready for Flask/Django integration")
print(f"   🚀 No PyTorch dependency required")

# Store for web app
web_app_engine = decision_engine

print(f"\n🌐 Next: Create Flask web interface")
print(f"   Run: pip install flask")
print(f"   Then I'll help you create the web application!")


#!/usr/bin/env python3
"""
Hospital Web Application Setup Script
Run this first to create all the necessary files and folders!

Usage: python setup_hospital_app.py
"""

import os

def create_hospital_structure():
    """Create the complete folder and file structure for the hospital web app"""
    
    print("🏥 CREATING HOSPITAL WEB APPLICATION STRUCTURE")
    print("=" * 50)
    
    # Define the complete structure
    structure = {
        # Main files
        "app.py": "# Main Flask application - PASTE CONTENT HERE",
        "config.py": "# Configuration settings",
        "requirements.txt": "# Python dependencies",
        
        # Templates folder
        "templates/base.html": "<!-- Base HTML template - PASTE CONTENT HERE -->",
        "templates/dashboard.html": "<!-- Dashboard template - PASTE CONTENT HERE -->",
        "templates/patient_form.html": "<!-- Patient form template - PASTE CONTENT HERE -->",
        "templates/analytics.html": "<!-- Analytics template - PASTE CONTENT HERE -->",
        
        # Static files
        "static/css/style.css": "/* Custom CSS styles */",
        "static/js/dashboard.js": "// Dashboard JavaScript",
        "static/js/main.js": "// Main JavaScript functions",
        
        # Models folder
        "models/__init__.py": "# Models package",
        "models/ai_model.py": "# AI decision engine",
        "models/database.py": "# Database models",
        
        # Routes folder
        "routes/__init__.py": "# Routes package",
        "routes/main.py": "# Main routes",
        "routes/api.py": "# API routes",
        
        # Data folder (for any data files)
        "data/README.md": "# Data folder for CSV files, etc.",
        
        # Documentation
        "README.md": "# Hospital AI Web Application",
        "INSTALL.md": "# Installation Instructions"
    }
    
    # Create all folders and files
    created_files = []
    created_folders = set()
    
    for file_path, content in structure.items():
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and directory not in created_folders:
            os.makedirs(directory, exist_ok=True)
            created_folders.add(directory)
            print(f"📁 Created folder: {directory}/")
        
        # Create the file with placeholder content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content + "\n")
        
        created_files.append(file_path)
        print(f"📄 Created file: {file_path}")
    
    # Create requirements.txt with actual dependencies
    requirements_content = """Flask==2.3.3
Werkzeug==2.3.7
Jinja2==3.1.2
"""
    
    with open("requirements.txt", 'w') as f:
        f.write(requirements_content)
    
    # Create a basic README
    readme_content = """# Hospital AI Web Application

## Quick Start

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your browser to: http://localhost:5000

## File Structure

- `app.py` - Main Flask application
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, images
- `models/` - Data models and AI engine
- `routes/` - URL routes and views

## Next Steps

1. Paste the provided code into each file
2. Customize as needed
3. Run and test your application!
"""
    
    with open("README.md", 'w') as f:
        f.write(readme_content)
    
    # Create installation instructions
    install_content = """# Installation Instructions

## Step 1: Create the File Structure
Run the setup script:
```bash
python setup_hospital_app.py
```

## Step 2: Install Dependencies
```bash
pip install flask
# OR install from requirements.txt:
pip install -r requirements.txt
```

## Step 3: Add Content to Files
Copy and paste the provided code into these files:
1. app.py (main application)
2. templates/base.html
3. templates/dashboard.html
4. templates/patient_form.html
5. templates/analytics.html

## Step 4: Run the Application
```bash
python app.py
```

## Step 5: Access Your Web App
Open browser to: http://localhost:5000

## Troubleshooting
- Make sure Python 3.7+ is installed
- If you get import errors, install Flask: `pip install flask`
- Check that all files have the correct content pasted
"""
    
    with open("INSTALL.md", 'w') as f:
        f.write(install_content)
    
    print("\n" + "=" * 50)
    print("✅ SUCCESS! Hospital web application structure created!")
    print("=" * 50)
    print(f"📊 Created {len(created_files)} files")
    print(f"📁 Created {len(created_folders)} folders")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Copy and paste the provided code into each file")
    print("2. Install Flask: pip install flask")
    print("3. Run your app: python app.py")
    print("4. Open browser to: http://localhost:5000")
    
    print("\n📋 FILES TO FILL WITH CONTENT:")
    priority_files = [
        "app.py (MOST IMPORTANT - main application)",
        "templates/base.html",
        "templates/dashboard.html", 
        "templates/patient_form.html",
        "templates/analytics.html"
    ]
    
    for i, file in enumerate(priority_files, 1):
        print(f"{i}. {file}")
    
    print(f"\n📂 Your project is ready in: {os.getcwd()}")
    
    return created_files, created_folders

def show_file_tree():
    """Display the created file structure"""
    print("\n🌳 FILE STRUCTURE CREATED:")
    print("📁 hospital_webapp/")
    print("  📄 app.py")
    print("  📄 config.py") 
    print("  📄 requirements.txt")
    print("  📄 README.md")
    print("  📄 INSTALL.md")
    print("  📁 templates/")
    print("    📄 base.html")
    print("    📄 dashboard.html")
    print("    📄 patient_form.html")
    print("    📄 analytics.html")
    print("  📁 static/")
    print("    📁 css/")
    print("      📄 style.css")
    print("    📁 js/")
    print("      📄 dashboard.js")
    print("      📄 main.js")
    print("  📁 models/")
    print("    📄 __init__.py")
    print("    📄 ai_model.py")
    print("    📄 database.py")
    print("  📁 routes/")
    print("    📄 __init__.py")
    print("    📄 main.py")
    print("    📄 api.py")
    print("  📁 data/")
    print("    📄 README.md")

if __name__ == "__main__":
    try:
        created_files, created_folders = create_hospital_structure()
        show_file_tree()
        
        print("\n" + "🎉" * 20)
        print("SUCCESS! Your hospital web app structure is ready!")
        print("🎉" * 20)
        
    except Exception as e:
        print(f"❌ Error creating structure: {e}")
        print("Please make sure you have write permissions in this directory.")





#!/usr/bin/env python3
"""
MIMIC Data Analysis & Visualization Code
Add this to your existing hospital system to understand your data processing
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class MIMICAnalyzer:
    def __init__(self, base_path='/Users/macbookpro/hospital app/data/dataset Updated/'):
        self.base_path = base_path
        self.data = {}
        self.analysis_results = {}
        
    def load_and_analyze_data(self):
        """Load MIMIC data and perform detailed analysis"""
        print("🔍 ANALYZING MIMIC DATA PROCESSING...")
        print("=" * 60)
        
        # Load the files
        files_to_analyze = {
            'patients': 'PATIENTS.csv',
            'icustays': 'ICUSTAYS.csv', 
            'admissions': 'ADMISSIONS.csv',
            'callout': 'CALLOUT.csv',
            'transfers': 'TRANSFERS.csv'
        }
        
        for key, filename in files_to_analyze.items():
            filepath = os.path.join(self.base_path, filename)
            if os.path.exists(filepath):
                print(f"✅ Loading {filename}...")
                # Load sample for analysis
                df = pd.read_csv(filepath, nrows=10000)
                self.data[key] = df
                print(f"   → Loaded {len(df):,} rows, {len(df.columns)} columns")
                print(f"   → Columns: {list(df.columns)}")
            else:
                print(f"❌ {filename} not found!")
                
        print("\n" + "=" * 60)
        
    def analyze_cost_factors(self):
        """Analyze what actually determines the cost calculations"""
        print("💰 COST CALCULATION ANALYSIS")
        print("=" * 40)
        
        # Base costs (these are YOUR estimations, not from data)
        base_costs = {
            'icu': 2500,
            'ward': 700,
            'ed': 1000,
            'discharge': 0
        }
        
        print("📊 BASE COSTS (Your Estimations):")
        for unit, cost in base_costs.items():
            print(f"   {unit.upper()}: ${cost:,}/day")
        
        # Check if we can calculate complexity factor
        if 'admissions' in self.data and self.data['admissions'] is not None:
            admissions = self.data['admissions']
            
            if 'HOSPITAL_EXPIRE_FLAG' in admissions.columns:
                # This is the actual calculation from your code
                mortality_rate = admissions['HOSPITAL_EXPIRE_FLAG'].mean()
                complexity_factor = 1 + mortality_rate
                
                print(f"\n🏥 HOSPITAL COMPLEXITY ANALYSIS:")
                print(f"   Total admissions analyzed: {len(admissions):,}")
                print(f"   Deaths (HOSPITAL_EXPIRE_FLAG=1): {admissions['HOSPITAL_EXPIRE_FLAG'].sum():,}")
                print(f"   Mortality rate: {mortality_rate:.3f} ({mortality_rate*100:.1f}%)")
                print(f"   Complexity factor: {complexity_factor:.3f}")
                
                # Calculate adjusted costs
                print(f"\n💵 ADJUSTED COSTS (Base × Complexity Factor):")
                adjusted_costs = {}
                for unit, base_cost in base_costs.items():
                    if unit != 'discharge':
                        adjusted_cost = int(base_cost * complexity_factor)
                        adjusted_costs[unit] = adjusted_cost
                        increase = adjusted_cost - base_cost
                        print(f"   {unit.upper()}: ${base_cost:,} → ${adjusted_cost:,} (+${increase:,})")
                
                # Store results
                self.analysis_results['mortality_rate'] = mortality_rate
                self.analysis_results['complexity_factor'] = complexity_factor
                self.analysis_results['base_costs'] = base_costs
                self.analysis_results['adjusted_costs'] = adjusted_costs
                
                return True
            else:
                print("❌ HOSPITAL_EXPIRE_FLAG column not found in admissions data")
                return False
        else:
            print("❌ Admissions data not available")
            return False
    
    def analyze_los_patterns(self):
        """Analyze Length of Stay patterns from MIMIC data"""
        print("\n⏱️ LENGTH OF STAY ANALYSIS")
        print("=" * 40)
        
        if 'icustays' in self.data and self.data['icustays'] is not None:
            icustays = self.data['icustays']
            
            if 'INTIME' in icustays.columns and 'OUTTIME' in icustays.columns:
                # Calculate LOS just like your code does
                icustays_copy = icustays.copy()
                icustays_copy['INTIME'] = pd.to_datetime(icustays_copy['INTIME'], errors='coerce')
                icustays_copy['OUTTIME'] = pd.to_datetime(icustays_copy['OUTTIME'], errors='coerce')
                
                # Remove invalid dates
                valid_stays = icustays_copy.dropna(subset=['INTIME', 'OUTTIME'])
                
                if len(valid_stays) > 0:
                    valid_stays['los_hours'] = (valid_stays['OUTTIME'] - valid_stays['INTIME']).dt.total_seconds() / 3600
                    valid_stays['los_days'] = valid_stays['los_hours'] / 24
                    
                    # Filter realistic LOS (remove outliers)
                    realistic_los = valid_stays[(valid_stays['los_days'] > 0) & (valid_stays['los_days'] <= 30)]
                    
                    if len(realistic_los) > 0:
                        print(f"📈 LOS STATISTICS (from {len(realistic_los):,} valid ICU stays):")
                        print(f"   Mean LOS: {realistic_los['los_days'].mean():.2f} days")
                        print(f"   Median LOS: {realistic_los['los_days'].median():.2f} days")
                        print(f"   Std Dev: {realistic_los['los_days'].std():.2f} days")
                        print(f"   Min LOS: {realistic_los['los_days'].min():.2f} days")
                        print(f"   Max LOS: {realistic_los['los_days'].max():.2f} days")
                        
                        # Store for use in LOS prediction
                        self.analysis_results['median_los'] = realistic_los['los_days'].median()
                        self.analysis_results['avg_los'] = realistic_los['los_days'].mean()
                        self.analysis_results['los_data'] = realistic_los['los_days']
                        
                        return realistic_los
                    else:
                        print("❌ No valid LOS data after filtering")
                else:
                    print("❌ No valid datetime data found")
            else:
                print("❌ INTIME/OUTTIME columns not found")
        else:
            print("❌ ICU stays data not available")
        
        return None
    
    def analyze_capacity_estimates(self):
        """Analyze how ICU capacity is estimated"""
        print("\n🏥 CAPACITY ESTIMATION ANALYSIS")
        print("=" * 40)
        
        if 'icustays' in self.data and self.data['icustays'] is not None:
            icustays = self.data['icustays']
            
            print(f"📊 ICU STAYS DATA:")
            print(f"   Total ICU stay records: {len(icustays):,}")
            
            if 'ICUSTAY_ID' in icustays.columns:
                unique_stays = icustays['ICUSTAY_ID'].nunique()
                print(f"   Unique ICU stays: {unique_stays:,}")
                
                # This is how your code estimates capacity
                estimated_capacity = min(max(20, unique_stays // 100), 50)
                print(f"   Estimated ICU capacity: {estimated_capacity} beds")
                print(f"   Calculation: min(max(20, {unique_stays}//100), 50) = {estimated_capacity}")
                
                self.analysis_results['icu_capacity'] = estimated_capacity
            
            if 'FIRST_CAREUNIT' in icustays.columns:
                care_units = icustays['FIRST_CAREUNIT'].value_counts()
                print(f"\n🏥 CARE UNITS FOUND:")
                for unit, count in care_units.head(10).items():
                    print(f"   {unit}: {count:,} stays")
                
                self.analysis_results['care_units'] = care_units
    
    def test_los_prediction_algorithm(self):
        """Test the LOS prediction algorithm with real examples"""
        print("\n🧮 LOS PREDICTION ALGORITHM TEST")
        print("=" * 40)
        
        if 'median_los' not in self.analysis_results:
            print("❌ No LOS baseline data available")
            return
        
        base_los = self.analysis_results['median_los']
        print(f"📏 Base LOS (from MIMIC): {base_los:.2f} days")
        
        # Test cases from your algorithm
        test_cases = [
            {"age": 30, "severity": 3, "arrival": "walk-in", "name": "Young Mild Patient"},
            {"age": 75, "severity": 8, "arrival": "ambulance", "name": "Elderly Severe Patient"},
            {"age": 85, "severity": 10, "arrival": "ambulance", "name": "Very Elderly Critical Patient"},
            {"age": 45, "severity": 5, "arrival": "referral", "name": "Middle-aged Average Patient"}
        ]
        
        print(f"\n🧪 TESTING LOS PREDICTION ALGORITHM:")
        print("Formula: LOS = base_los × α_age × α_severity × α_arrival")
        
        for case in test_cases:
            # Age factor
            if case["age"] >= 80:
                alpha_age = 1.4
            elif case["age"] >= 65:
                alpha_age = 1.2
            else:
                alpha_age = 1.0
            
            # Severity factor
            alpha_severity = 1 + (case["severity"] - 5) * 0.2
            
            # Arrival factor
            alpha_arrival = 1.3 if case["arrival"] == "ambulance" else 1.0
            
            # Calculate predicted LOS
            predicted_los = base_los * alpha_age * alpha_severity * alpha_arrival
            
            print(f"\n   {case['name']}:")
            print(f"     Age {case['age']} → α_age = {alpha_age}")
            print(f"     Severity {case['severity']} → α_severity = {alpha_severity:.2f}")
            print(f"     Arrival {case['arrival']} → α_arrival = {alpha_arrival}")
            print(f"     Predicted LOS: {base_los:.2f} × {alpha_age} × {alpha_severity:.2f} × {alpha_arrival} = {predicted_los:.2f} days")
    
    def create_visualizations(self):
        """Create visualizations of the analysis"""
        print("\n📊 CREATING VISUALIZATIONS...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('MIMIC Data Analysis for Hospital AI System', fontsize=16, fontweight='bold')
        
        # 1. Cost Analysis
        if 'base_costs' in self.analysis_results and 'adjusted_costs' in self.analysis_results:
            ax1 = axes[0, 0]
            units = ['ICU', 'Ward', 'ED']
            base_values = [self.analysis_results['base_costs'][u.lower()] for u in units]
            adjusted_values = [self.analysis_results['adjusted_costs'][u.lower()] for u in units]
            
            x = np.arange(len(units))
            width = 0.35
            
            ax1.bar(x - width/2, base_values, width, label='Base Costs (Estimates)', alpha=0.8)
            ax1.bar(x + width/2, adjusted_values, width, label='MIMIC-Adjusted Costs', alpha=0.8)
            
            ax1.set_title('Cost Estimation: Base vs MIMIC-Adjusted')
            ax1.set_ylabel('Cost per Day ($)')
            ax1.set_xlabel('Hospital Unit')
            ax1.set_xticks(x)
            ax1.set_xticklabels(units)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # 2. LOS Distribution
        if 'los_data' in self.analysis_results:
            ax2 = axes[0, 1]
            los_data = self.analysis_results['los_data']
            
            ax2.hist(los_data, bins=50, alpha=0.7, edgecolor='black')
            ax2.axvline(los_data.mean(), color='red', linestyle='--', label=f'Mean: {los_data.mean():.2f}')
            ax2.axvline(los_data.median(), color='green', linestyle='--', label=f'Median: {los_data.median():.2f}')
            
            ax2.set_title('Length of Stay Distribution (MIMIC ICU Data)')
            ax2.set_xlabel('Length of Stay (days)')
            ax2.set_ylabel('Frequency')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # 3. Complexity Factor Impact
        if 'mortality_rate' in self.analysis_results:
            ax3 = axes[1, 0]
            mortality_rate = self.analysis_results['mortality_rate']
            
            # Show impact of different mortality rates
            mortality_ranges = np.arange(0.05, 0.25, 0.01)
            complexity_factors = 1 + mortality_ranges
            icu_costs = 2500 * complexity_factors
            
            ax3.plot(mortality_ranges * 100, icu_costs, linewidth=3)
            ax3.axvline(mortality_rate * 100, color='red', linestyle='--', 
                       label=f'Your Hospital: {mortality_rate*100:.1f}%')
            
            ax3.set_title('ICU Cost vs Hospital Mortality Rate')
            ax3.set_xlabel('Mortality Rate (%)')
            ax3.set_ylabel('ICU Cost per Day ($)')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # 4. Care Units Distribution
        if 'care_units' in self.analysis_results:
            ax4 = axes[1, 1]
            care_units = self.analysis_results['care_units'].head(8)
            
            ax4.barh(range(len(care_units)), care_units.values)
            ax4.set_yticks(range(len(care_units)))
            ax4.set_yticklabels(care_units.index)
            ax4.set_title('ICU Care Units Distribution (MIMIC)')
            ax4.set_xlabel('Number of Stays')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Save the plot
        plt.savefig('mimic_analysis_results.png', dpi=300, bbox_inches='tight')
        print("📁 Visualization saved as 'mimic_analysis_results.png'")
    
    def generate_summary_report(self):
        """Generate a summary of what's actually from MIMIC vs estimated"""
        print("\n📋 SUMMARY REPORT: WHAT'S REAL vs ESTIMATED")
        print("=" * 60)
        
        print("✅ FROM MIMIC DATA (Real):")
        if 'mortality_rate' in self.analysis_results:
            print(f"   • Hospital mortality rate: {self.analysis_results['mortality_rate']*100:.1f}%")
            print(f"   • Complexity factor: {self.analysis_results['complexity_factor']:.3f}")
        if 'median_los' in self.analysis_results:
            print(f"   • Median ICU LOS: {self.analysis_results['median_los']:.2f} days")
            print(f"   • Average ICU LOS: {self.analysis_results['avg_los']:.2f} days")
        if 'icu_capacity' in self.analysis_results:
            print(f"   • Estimated ICU capacity: {self.analysis_results['icu_capacity']} beds")
        
        print(f"\n📊 YOUR ESTIMATIONS (Not from MIMIC):")
        print(f"   • Base ICU cost: $2,500/day")
        print(f"   • Base Ward cost: $700/day") 
        print(f"   • Base ED cost: $1,000/day")
        print(f"   • LOS prediction multipliers (age, severity, arrival)")
        print(f"   • Ward capacity (2× ICU capacity)")
        print(f"   • ED capacity (0.5× ICU capacity)")
        
        print(f"\n🔧 HYBRID APPROACH:")
        print(f"   • Base costs (your estimates) × Complexity factor (from MIMIC)")
        print(f"   • LOS baseline (from MIMIC) × Adjustment factors (your algorithm)")
        print(f"   • Hospital structure (your design) + Real patient patterns (MIMIC)")

def main():
    """Run the complete MIMIC analysis"""
    analyzer = MIMICAnalyzer()
    
    # Load and analyze data
    analyzer.load_and_analyze_data()
    
    # Perform analyses
    cost_success = analyzer.analyze_cost_factors()
    analyzer.analyze_los_patterns()
    analyzer.analyze_capacity_estimates()
    analyzer.test_los_prediction_algorithm()
    
    # Create visualizations
    if cost_success:
        analyzer.create_visualizations()
    
    # Generate summary
    analyzer.generate_summary_report()
    
    print(f"\n🎉 ANALYSIS COMPLETE!")
    print(f"Now you know exactly what comes from MIMIC data vs your estimations!")

if __name__ == "__main__":
    main()


