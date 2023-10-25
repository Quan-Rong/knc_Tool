import streamlit as st
import pandas as pd
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import linregress
import numpy as np
from PIL import Image

st.set_page_config(page_title="✈️K&C Simulation Results PostProcess", page_icon="📈", layout="wide")

bump_image=Image.open('logo_bump_01.JPG')
bump_image_02=Image.open('logo_bump_02.JPG')
st.image(bump_image, caption='Version: Beta V0.2', use_column_width='always')

st.sidebar.title('K&C Bump Test')
st.sidebar.markdown('---')
st.sidebar.image(bump_image_02, caption='Adams/Car')

#程序中，所有的变量都以bump_开头用以区分

def main():
    st.title("K&C Test - Body Bounce")
    # Erklärung
    bump_description_col1, bump_description_col2 = st.columns([3, 1])
        
    with bump_description_col1:
        st.markdown("* Body is displaced vertically")
        st.markdown("* Wheel pads 'float' (force controlled to zero load) horizontally and in rotation")
        st.markdown("* Steering angle is fixed")
        st.markdown("* Bounce and rebound limits and cycle time can be specified")
        st.markdown("* Key results are: **Wheel Rate**, **Bump Steer**, **Bump Camber**, **Track Change**, **Wheel Recession**")
                   
    with bump_description_col2:
        st.image(bump_image_02, caption='Adams/Car')
        

    bump_uploaded_file = st.file_uploader("Choose a .res file", type=[".res"])

    if bump_uploaded_file:
        bump_content = bump_uploaded_file.read().decode('utf-8')
        bump_blocks = bump_extract_blocks(bump_content)
        
        if bump_blocks:
            bump_process_blocks(bump_blocks)
        else:
            st.write("No valid data blocks found in the file.")

def bump_extract_blocks(bump_content):
    bump_pattern = r'<Step type="quasiStatic">([\s\S]*?)</Step>'
    bump_blocks = re.findall(bump_pattern, bump_content)
    return bump_blocks

def bump_process_blocks(bump_blocks):
    # Extract values using the provided method
    bump_wheel_travel_li = [float(bump_block.split()[918]) for bump_block in bump_blocks]
    bump_wheel_travel_re = [float(bump_block.split()[919]) for bump_block in bump_blocks]
    #
    bump_toe_li = [float(bump_block.split()[1025])*180/3.1415926 for bump_block in bump_blocks]
    bump_toe_re = [float(bump_block.split()[1026])*180/3.1415926 for bump_block in bump_blocks]
    #
    bump_camber_li = [float(bump_block.split()[1027])*180/3.1415926 for bump_block in bump_blocks]
    bump_camber_re = [float(bump_block.split()[1028])*180/3.1415926 for bump_block in bump_blocks]
    #
    bump_vertical_force_li = [float(bump_block.split()[934]) for bump_block in bump_blocks]
    bump_vertical_force_re = [float(bump_block.split()[935]) for bump_block in bump_blocks]
    # 
    bump_wheel_base_li = [float(bump_block.split()[922]) for bump_block in bump_blocks]
    bump_wheel_base_re = [float(bump_block.split()[923]) for bump_block in bump_blocks]
    # 
    bump_tire_cp_y_li = [float(bump_block.split()[1057]) for bump_block in bump_blocks]
    bump_tire_cp_y_re = [float(bump_block.split()[1062]) for bump_block in bump_blocks]

    # Create DataFrame
    df_bump = pd.DataFrame({
        'bump_wheel_travel_li': bump_wheel_travel_li,
        'bump_wheel_travel_re': bump_wheel_travel_re,
        'bump_toe_li': bump_toe_li,
        'bump_toe_re': bump_toe_re,
        'bump_camber_li': bump_camber_li,
        'bump_camber_re': bump_camber_re,
        'bump_vertical_force_li': bump_vertical_force_li,
        'bump_vertical_force_re': bump_vertical_force_re,
        'bump_wheel_base_li': bump_wheel_base_li,
        'bump_wheel_base_re': bump_wheel_base_re,
        'bump_tire_cp_y_li': bump_tire_cp_y_li,
        'bump_tire_cp_y_re': bump_tire_cp_y_re
    })

    # Find the row where bump_wheel_travel_li is closest to 0
    offset_row = df_bump.iloc[(df_bump['bump_wheel_travel_li']).abs().idxmin()]
    
    # Subtract the values of this row from the entire DataFrame to create df_bump_offset
    df_bump_offset = df_bump.subtract(offset_row)

    st.write(f"Number of available data blocks = {len(bump_blocks)}")
    
    # Display columns in multiselect
    selected_columns = st.multiselect("Select columns:", df_bump_offset.columns.tolist(), default=df_bump_offset.columns.tolist())

    # Display selected columns from df_bump_offset
    if selected_columns:
        st.dataframe(df_bump_offset[selected_columns], width= 2400, height= 300)
    
    # Plotting
    if st.button("Plot Graphs (Bump Test)"):
        
        #定义要在按下后输出的内容
        (
            fig_bump_wheel_rate, fig_bump_steer, fig_bump_camber, fig_bump_wheel_base_change, fig_bump_track_change, 
            slope_bump_wheel_rate_li, slope_bump_wheel_rate_re, 
            slope_bump_steer_li, slope_bump_steer_re, 
            slope_bump_camber_li, slope_bump_camber_re, 
            slope_bump_wheel_base_change_li, slope_bump_wheel_base_change_re,
            slope_bump_track_change_li, slope_bump_track_change_re
        ) = plot_graphs(df_bump_offset, df_bump)
        
        # fig_steer, fig_camber, slope_li, slope_re, slope_camber_li, slope_camber_re = plot_graphs(df_bump_offset)
        
        fig_bump_wheel_rate.update_layout(title_text="Bump Wheel Rate: [N/mm]", title_font=dict(size=24, family="Arial Bold"), width=1600, height=800)
        fig_bump_steer.update_layout(title_text="Bump Steer: [deg/mm]", title_font=dict(size=24, family="Arial Bold"), width=1600, height=800)
        fig_bump_camber.update_layout(title_text="Bump Camber: [deg/mm]", title_font=dict(size=24, family="Arial Bold"), width=1600, height=800)
        fig_bump_wheel_base_change.update_layout(title_text="Wheel Recession: [mm/mm]", title_font=dict(size=24, family="Arial Bold"), width=1600, height=800)
        fig_bump_track_change.update_layout(title_text="Track Change: [mm/mm]", title_font=dict(size=24, family="Arial Bold"), width=1600, height=800)
        
        # Create DataFrame for results
        bump_results = pd.DataFrame({
            'Parameter': [
                'bump_Wheel_Rate_li', 'bump_Wheel_Rate_re',
                'bump_Toe_Change_li', 'bump_Toe_Change_re', 
                'bump_Camber_Change_li', 'bump_Camber_Change_re',
                'bump_Wheel_Base_change_li', 'bump_Wheel_Base_Change_re',
                'bump_Track_Change_li', 'bump_Track_Change_re'
                ],
            'Slope': [
                slope_bump_wheel_rate_li, slope_bump_wheel_rate_re,
                slope_bump_steer_li, slope_bump_steer_re, 
                slope_bump_camber_li, slope_bump_camber_re, 
                slope_bump_wheel_base_change_li, slope_bump_wheel_base_change_re,
                slope_bump_track_change_li, slope_bump_track_change_re
                ]
        })

        # Display the DataFrame in Streamlit
        #st.table(bump_results.T.astype(str))
        st.table(bump_results.round(4).T.astype(str))
        
        # sidebar display
        st.sidebar.title('Key Results Overview:')
        st.sidebar.markdown('---')
        st.sidebar.table(bump_results.iloc[::2].round(4).astype(str))
        if st.sidebar.button('Save CSV'):
            bump_results.iloc[::2].to_csv('bump_results_odd_rows.csv', index=False)
            st.sidebar.write('File saved as bump_results_odd_rows.csv')
        
        # Update layout for fig_bump_wheel_rate
        fig_bump_wheel_rate.update_layout(
            xaxis_title_font=dict(size=18, family='Arial Bold'), 
            yaxis_title_font=dict(size=18, family='Arial Bold'),
            xaxis_tickfont=dict(size=18, family='Arial Bold'),
            yaxis_tickfont=dict(size=18, family='Arial Bold'),
            legend_font=dict(size=18, family='Arial Bold')
        )
        # Do the same for the second xaxis and yaxis (for the right subplot)
        fig_bump_wheel_rate.update_layout(
            xaxis2_title_font=dict(size=18, family='Arial Bold'), 
            yaxis2_title_font=dict(size=18, family='Arial Bold'),
            xaxis2_tickfont=dict(size=18, family='Arial Bold'),
            yaxis2_tickfont=dict(size=18, family='Arial Bold')
        )
        
        # Update layout for fig_bump_steer
        fig_bump_steer.update_layout(
            xaxis_title_font=dict(size=18, family='Arial Bold'), 
            yaxis_title_font=dict(size=18, family='Arial Bold'),
            xaxis_tickfont=dict(size=18, family='Arial Bold'),
            yaxis_tickfont=dict(size=18, family='Arial Bold'),
            legend_font=dict(size=18, family='Arial Bold')
        )
        # Do the same for the second xaxis and yaxis (for the right subplot)
        fig_bump_steer.update_layout(
            xaxis2_title_font=dict(size=18, family='Arial Bold'), 
            yaxis2_title_font=dict(size=18, family='Arial Bold'),
            xaxis2_tickfont=dict(size=18, family='Arial Bold'),
            yaxis2_tickfont=dict(size=18, family='Arial Bold')
        )

        # Update layout for fig_bump_camber
        fig_bump_camber.update_layout(
            xaxis_title_font=dict(size=18, family='Arial Bold'), 
            yaxis_title_font=dict(size=18, family='Arial Bold'),
            xaxis_tickfont=dict(size=18, family='Arial Bold'),
            yaxis_tickfont=dict(size=18, family='Arial Bold'),
            legend_font=dict(size=18, family='Arial Bold')
        )
        # Do the same for the second xaxis and yaxis (for the right subplot)
        fig_bump_camber.update_layout(
            xaxis2_title_font=dict(size=18, family='Arial Bold'), 
            yaxis2_title_font=dict(size=18, family='Arial Bold'),
            xaxis2_tickfont=dict(size=18, family='Arial Bold'),
            yaxis2_tickfont=dict(size=18, family='Arial Bold')
        )
        
         # Update layout for fig_bump_wheel_base_change
        fig_bump_wheel_base_change.update_layout(
            xaxis_title_font=dict(size=18, family='Arial Bold'), 
            yaxis_title_font=dict(size=18, family='Arial Bold'),
            xaxis_tickfont=dict(size=18, family='Arial Bold'),
            yaxis_tickfont=dict(size=18, family='Arial Bold'),
            legend_font=dict(size=18, family='Arial Bold')
        )
        # Do the same for the second xaxis and yaxis (for the right subplot)
        fig_bump_wheel_base_change.update_layout(
            xaxis2_title_font=dict(size=18, family='Arial Bold'), 
            yaxis2_title_font=dict(size=18, family='Arial Bold'),
            xaxis2_tickfont=dict(size=18, family='Arial Bold'),
            yaxis2_tickfont=dict(size=18, family='Arial Bold')
        )
        
         # Update layout for fig_bump_track_change
        fig_bump_track_change.update_layout(
            xaxis_title_font=dict(size=18, family='Arial Bold'), 
            yaxis_title_font=dict(size=18, family='Arial Bold'),
            xaxis_tickfont=dict(size=18, family='Arial Bold'),
            yaxis_tickfont=dict(size=18, family='Arial Bold'),
            legend_font=dict(size=18, family='Arial Bold')
        )
        # Do the same for the second xaxis and yaxis (for the right subplot)
        fig_bump_track_change.update_layout(
            xaxis2_title_font=dict(size=18, family='Arial Bold'), 
            yaxis2_title_font=dict(size=18, family='Arial Bold'),
            xaxis2_tickfont=dict(size=18, family='Arial Bold'),
            yaxis2_tickfont=dict(size=18, family='Arial Bold')
        )
        
        # Update background color for fig_bump_wheel_rate
        fig_bump_wheel_rate.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            xaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray')
        )

        # Update background color for fig_bump_steer
        fig_bump_steer.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            xaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray')
        )

        # Update background color for fig_bump_camber
        fig_bump_camber.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            xaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray')
        )
        
        # Update background color for fig_wheel_base_change
        fig_bump_wheel_base_change.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            xaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray')
        )
        
        # Update background color for fig_bump_track_change
        fig_bump_track_change.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            xaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray')
        )
        st.markdown('---')
        st.markdown("""
                ### Wheel Rate
                * Wheel rate curve defines the **suspension stiffness** and hence the **ride frequency**. Ride frequency determines body control and comfort levels. Relative ride frequency between front and rear axles determindes body pitch behaviour.
                * Bump stop/spring-aid contact and progression is illustrated. Sharp increases in wheel rate give abruptness in ride.
                * Wheel rate due to suspension bushes is a good indicator of suspension hysteresis, which affects secondary ride comfort. ***(not shown in Adams/car model)***
                * High hysteresis from sliding friction and bush internal friction gives poor secondary ride performance (good ride hysteresis <5% of static load, poor ride >15%). (not shown in Adams/car model)
                """)
        st.plotly_chart(fig_bump_wheel_rate)
        
        # Display the regression line equations
        bump_wheel_rate_col1, bump_wheel_rate_col2, bump_wheel_rate_col3 = st.columns([1, 1, 1])
        
        with bump_wheel_rate_col1:
            st.markdown("**Curve Fitting Left  (-10mm <-> +10mm ) [N/mm]:**")
            st.text_input(label="", value=f"{slope_bump_wheel_rate_li:.4f}", key="result_display_bump_wheel_rate_li") 
                   
        with bump_wheel_rate_col2:
            st.markdown("**Curve Fitting Right  (-10mm <-> +10mm ) [N/mm]:**")
            st.text_input(label="", value=f"{slope_bump_wheel_rate_re:.4f}", key="result_display_bump_wheel_rate_re")
            
        
        
        st.markdown('---')
        st.markdown("""
                ### Bump Steer
                * Excessive bump steer causes path deviation and wheel fight over rough road surfaces. It alos contributes to steer behaviour when braking in corners.
                """)
        
        st.plotly_chart(fig_bump_steer)
        
        # Display the regression line equations
        bump_steer_col1, bump_steer_col2, bump_steer_col3 = st.columns([1, 1, 1])
        
        with bump_steer_col1:
            st.markdown("**Curve Fitting Left  (-10mm <-> +10mm ) [deg/m]:**")
            st.text_input(label="", value=f"{slope_bump_steer_li * 1000:.4f}", key="result_display_bump_steer_li") 
                   
        with bump_steer_col2:
            st.markdown("**Curve Fitting Right  (-10mm <-> +10mm ) [deg/m]:**")
            st.text_input(label="", value=f"{slope_bump_steer_re * 1000:.4f}", key="result_display_bump_steer_re")
            
        
        
        st.markdown('---')
        st.markdown("""
                ### Bump Camber
                * Excessive bump camber will contributes to path deviation for single wheel or asymmetric inputs across the axles.
                * Braking performance of passenger car tyres is relatively insentitive to camber angle.
                """)
        
        st.plotly_chart(fig_bump_camber)
        
        # Display the regression line equations
        bump_camber_col1, bump_camber_col2, bump_camber_col3 = st.columns([1, 1, 1])
        
        with bump_camber_col1:
            st.markdown("**Curve Fitting Left  (-10mm <-> +10mm ) [deg/m]:**")
            st.text_input(label="", value=f"{slope_bump_camber_li * 1000:.4f}", key="result_display_bump_camber_li") 
                   
        with bump_camber_col2:
            st.markdown("**Curve Fitting Right  (-10mm <-> +10mm ) [deg/m]:**")
            st.text_input(label="", value=f"{slope_bump_camber_re * 1000:.4f}", key="result_display_bump_camber_re")
            
            
        
        st.markdown('---')
        st.markdown("""
                ### Bump Wheel Base Change
                * Forward movement of the front wheel during bump provides anti-dive and anti-lift characteristics, but reduces impact isolation.
                * Rearward movement of the rear wheel during bump provides anti-dive and anti-squat characteristics, and aligns with the requirement for impact isolation.
                """)
        
        st.plotly_chart(fig_bump_wheel_base_change)
        # Display the regression line equations
        bump_wheel_base_change_col1, bump_wheel_base_change_col2, bump_wheel_base_change_col3 = st.columns([1, 1, 1])
        
        with bump_wheel_base_change_col1:
            st.markdown("**Curve Fitting Left  (-10mm <-> +10mm ) [mm/m]:**")
            st.text_input(label="", value=f"{slope_bump_wheel_base_change_li * 1000:.4f}", key="result_display_bump_wheel_base_change_li") 
                   
        with bump_wheel_base_change_col2:
            st.markdown("**Curve Fitting Right  (-10mm <-> +10mm ) [mm/m]:**")
            st.text_input(label="", value=f"{slope_bump_wheel_base_change_re * 1000:.4f}", key="result_display_bump_wheel_base_change_re")
            
            
        
        st.markdown('---')
        st.markdown("""
                ### Bump Track Change
                * Large track changes cause path deviation, tyre wear and ride comfort problems.
                """)
        
        st.plotly_chart(fig_bump_track_change)
        # Display the regression line equations
        bump_track_change_col1, bump_track_change_col2, bump_track_change_col3 = st.columns([1, 1, 1])
        
        with bump_track_change_col1:
            st.markdown("**Curve Fitting Left  (-10mm <-> +10mm ) [mm/m]:**")
            st.text_input(label="", value=f"{slope_bump_track_change_li * 1000:.4f}", key="result_display_bump_wtrack_change_li") 
                   
        with bump_track_change_col2:
            st.markdown("**Curve Fitting Right  (-10mm <-> +10mm ) [mm/m]:**")
            st.text_input(label="", value=f"{slope_bump_track_change_re * 1000:.4f}", key="result_display_bump_track_change_re")
            
            


def plot_graphs(df_bump_offset, df_bump):
    
    # Create the 1. figure with subplots for Steer
    fig_bump_wheel_rate = make_subplots(rows=1, cols=2,
                              subplot_titles=('Bump Wheel Rate [N/mm]. Rear Left', 'Bump Wheel Rate [N/mm]. Rear Right'))
    
    # Create the 2. figure with subplots for Steer
    fig_bump_steer = make_subplots(rows=1, cols=2,
                              subplot_titles=('Bump Steer [deg/mm]. Rear Left', 'Bump Steer [deg/mm]. Rear Right'))
    
    # Create the 3. figure with subplots for Camber
    fig_bump_camber = make_subplots(rows=1, cols=2,
                               subplot_titles=('Bump Camber [deg/mm]. Rear Left', 'Bump Camber [deg/mm]. Rear Right'))
    
    # Create the 4. figure with subplots for Steer
    fig_bump_wheel_base_change = make_subplots(rows=1, cols=2,
                              subplot_titles=('Wheel Center X Displacement [mm/mm]. Rear Left', 'Wheel Center X Displacement [mm/mm]. Rear Right'))
    
    # Create the 5. figure with subplots for Steer
    fig_bump_track_change = make_subplots(rows=1, cols=2,
                              subplot_titles=('Contact Patch Y Displacement [mm/mm]. Rear Left', 'Contact Patch Y Displacement [mm/mm]. Rear Right'))
    
    
    

    # Filter data for linear regression
    bump_offset_mask_li = (df_bump_offset['bump_wheel_travel_li'] >= -10) & (df_bump_offset['bump_wheel_travel_li'] <= 10)
    bump_offset_mask_re = (df_bump_offset['bump_wheel_travel_re'] >= -10) & (df_bump_offset['bump_wheel_travel_re'] <= 10)
    
    # Filter data only for wheel rate linear regression
    bump_mask_li = (df_bump['bump_wheel_travel_li'] >= -10) & (df_bump['bump_wheel_travel_li'] <= 10)
    bump_mask_re = (df_bump['bump_wheel_travel_re'] >= -10) & (df_bump['bump_wheel_travel_re'] <= 10)    
    
    
    
    # Linear regression for Left wheel_rate
    slope_bump_wheel_rate_li, intercept_bump_wheel_rate_li, _, _, _ = linregress(df_bump[bump_mask_li]['bump_wheel_travel_li'], 
                                                            df_bump[bump_mask_li]['bump_vertical_force_li'])
    # Linear regression for Right wheel_rate
    slope_bump_wheel_rate_re, intercept_bump_wheel_rate_re, _, _, _ = linregress(df_bump[bump_mask_re]['bump_wheel_travel_re'], 
                                                            df_bump[bump_mask_re]['bump_vertical_force_re'])
    
    # Linear regression for Left Steer
    slope_bump_steer_li, intercept_bump_steer_li, _, _, _ = linregress(df_bump_offset[bump_offset_mask_li]['bump_wheel_travel_li'], 
                                                            df_bump_offset[bump_offset_mask_li]['bump_toe_li'])
    # Linear regression for Right Steer
    slope_bump_steer_re, intercept_bump_steer_re, _, _, _ = linregress(df_bump_offset[bump_offset_mask_re]['bump_wheel_travel_re'], 
                                                            df_bump_offset[bump_offset_mask_re]['bump_toe_re'])
    
    # Linear regression for Left Camber
    slope_bump_camber_li, intercept_bump_camber_li, _, _, _ = linregress(df_bump_offset[bump_offset_mask_li]['bump_wheel_travel_li'], 
                                                              df_bump_offset[bump_offset_mask_li]['bump_camber_li'])
    # Linear regression for Right Camber
    slope_bump_camber_re, intercept_bump_camber_re, _, _, _ = linregress(df_bump_offset[bump_offset_mask_re]['bump_wheel_travel_re'], 
                                                              df_bump_offset[bump_offset_mask_re]['bump_camber_re'])
    
    # Linear regression for Left wheel base change
    slope_bump_wheel_base_change_li, intercept_bump_wheel_base_change_li, _, _, _ = linregress(df_bump_offset[bump_offset_mask_li]['bump_wheel_travel_li'], 
                                                              df_bump_offset[bump_offset_mask_li]['bump_wheel_base_li'])
    # Linear regression for Right wheel base change
    slope_bump_wheel_base_change_re, intercept_bump_wheel_base_change_re, _, _, _ = linregress(df_bump_offset[bump_offset_mask_re]['bump_wheel_travel_re'], 
                                                              df_bump_offset[bump_offset_mask_re]['bump_wheel_base_re'])
    
    # Linear regression for Left track change
    slope_bump_track_change_li, intercept_bump_track_change_li, _, _, _ = linregress(df_bump_offset[bump_offset_mask_li]['bump_wheel_travel_li'], 
                                                              -1*df_bump_offset[bump_offset_mask_li]['bump_tire_cp_y_li'])
    # Linear regression for Right track change
    slope_bump_track_change_re, intercept_bump_track_change_re, _, _, _ = linregress(df_bump_offset[bump_offset_mask_re]['bump_wheel_travel_re'], 
                                                              df_bump_offset[bump_offset_mask_re]['bump_tire_cp_y_re'])
    
    # Left wheel rate plot
    fig_bump_wheel_rate.add_trace(go.Scatter(x=df_bump['bump_wheel_travel_li'], 
                                   y=df_bump['bump_vertical_force_li'],
                                   mode='lines+markers', name='Bump Wheel Rate Left'), 
                        row=1, col=1)
    # Regression line for Left Steer
    fig_bump_wheel_rate.add_trace(go.Scatter(x=np.linspace(-10, 10, 400), 
                                   y=slope_bump_wheel_rate_li * np.linspace(-10, 10, 400) + intercept_bump_wheel_rate_li,
                                   mode='lines', name=f"y={slope_bump_wheel_rate_li:.4f}x + {intercept_bump_wheel_rate_li:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=1)
    fig_bump_wheel_rate.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_wheel_rate_li:.4f}x + {intercept_bump_wheel_rate_li:.4f}",
            xref="x1", yref="y1",
            x=0, y=slope_bump_wheel_rate_li * 0 + intercept_bump_wheel_rate_li+2000,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )

    # Right wheel rate plot
    fig_bump_wheel_rate.add_trace(go.Scatter(x=df_bump['bump_wheel_travel_re'], 
                                   y=df_bump['bump_vertical_force_re'],
                                   mode='lines+markers', name='Bump Wheel Rate Right'), 
                        row=1, col=2)
    # Regression line for Right Steer
    fig_bump_wheel_rate.add_trace(go.Scatter(x=np.linspace(-10, 10, 400), 
                                   y=slope_bump_wheel_rate_re * np.linspace(-10, 10, 400) + intercept_bump_wheel_rate_re,
                                   mode='lines', name=f"y={slope_bump_wheel_rate_re:.4f}x + {intercept_bump_wheel_rate_re:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=2)
    fig_bump_wheel_rate.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_wheel_rate_re:.4f}x + {intercept_bump_wheel_rate_re:.4f}",
            xref="x2", yref="y2",
            x=0, y=slope_bump_wheel_rate_re * 0 + intercept_bump_wheel_rate_re+2000,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )    
    
    # Left Steer plot
    fig_bump_steer.add_trace(go.Scatter(x=df_bump_offset['bump_wheel_travel_li'], 
                                   y=df_bump_offset['bump_toe_li'],
                                   mode='lines+markers', name='Bump Steer Left'), 
                        row=1, col=1)
    # Regression line for Left Steer
    fig_bump_steer.add_trace(go.Scatter(x=np.linspace(-10, 10, 400), 
                                   y=slope_bump_steer_li * np.linspace(-10, 10, 400) + intercept_bump_steer_li,
                                   mode='lines', name=f"y={slope_bump_steer_li:.4f}x + {intercept_bump_steer_li:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=1)
    fig_bump_steer.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_steer_li:.4f}x + {intercept_bump_steer_li:.4f}",
            xref="x1", yref="y1",
            x=0, y=slope_bump_steer_li * 0 + intercept_bump_steer_li+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )

    # Right Steer plot
    fig_bump_steer.add_trace(go.Scatter(x=df_bump_offset['bump_wheel_travel_re'], 
                                   y=df_bump_offset['bump_toe_re'],
                                   mode='lines+markers', name='Bump Steer Right'), 
                        row=1, col=2)
    # Regression line for Right Steer
    fig_bump_steer.add_trace(go.Scatter(x=np.linspace(-10, 10, 400), 
                                   y=slope_bump_steer_re * np.linspace(-10, 10, 400) + intercept_bump_steer_re,
                                   mode='lines', name=f"y={slope_bump_steer_re:.4f}x + {intercept_bump_steer_re:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=2)
    fig_bump_steer.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_steer_re:.4f}x + {intercept_bump_steer_re:.4f}",
            xref="x2", yref="y2",
            x=0, y=slope_bump_steer_re * 0 + intercept_bump_steer_re+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )
    
    # Left Camber plot
    fig_bump_camber.add_trace(go.Scatter(x=df_bump_offset['bump_wheel_travel_li'], 
                                   y=df_bump_offset['bump_camber_li'],
                                   mode='lines+markers', name='Bump Camber Left'), 
                        row=1, col=1)
    # Regression line for Left Camber
    fig_bump_camber.add_trace(go.Scatter(x=np.linspace(-10, 10, 400), 
                                   y=slope_bump_camber_li * np.linspace(-10, 10, 400) + intercept_bump_camber_li,
                                   mode='lines', name=f"y={slope_bump_camber_li:.4f}x + {intercept_bump_camber_li:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=1)
    fig_bump_camber.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_camber_li:.4f}x + {intercept_bump_camber_li:.4f}",
            xref="x1", yref="y1",
            x=0, y=slope_bump_camber_li * 0 + intercept_bump_camber_li+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )

    # Right Camber plot
    fig_bump_camber.add_trace(go.Scatter(x=df_bump_offset['bump_wheel_travel_re'], 
                                   y=df_bump_offset['bump_camber_re'],
                                   mode='lines+markers', name='Bump Camber Right'), 
                        row=1, col=2)
    # Regression line for Right Camber
    fig_bump_camber.add_trace(go.Scatter(x=np.linspace(-10, 10, 400), 
                                   y=slope_bump_camber_re * np.linspace(-10, 10, 400) + intercept_bump_camber_re,
                                   mode='lines', name=f"y={slope_bump_camber_re:.4f}x + {intercept_bump_camber_re:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=2)
    fig_bump_camber.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_camber_re:.4f}x + {intercept_bump_camber_re:.4f}",
            xref="x2", yref="y2",
            x=0, y=slope_bump_camber_re * 0 + intercept_bump_camber_re+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )

    # Left wheel base change plot
    fig_bump_wheel_base_change.add_trace(go.Scatter(x=df_bump_offset['bump_wheel_travel_li'], 
                                   y=df_bump_offset['bump_wheel_base_li'],
                                   mode='lines+markers', name='Bump wheel_base_change Left'), 
                        row=1, col=1)
    # Regression line for Left wheel_base_change
    fig_bump_wheel_base_change.add_trace(go.Scatter(x=np.linspace(-10, 10, 400), 
                                   y=slope_bump_wheel_base_change_li * np.linspace(-10, 10, 400) + intercept_bump_wheel_base_change_li,
                                   mode='lines', name=f"y={slope_bump_wheel_base_change_li:.4f}x + {intercept_bump_wheel_base_change_li:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=1)
    fig_bump_wheel_base_change.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_wheel_base_change_li:.4f}x + {intercept_bump_wheel_base_change_li:.4f}",
            xref="x1", yref="y1",
            x=0, y=slope_bump_wheel_base_change_li * 0 + intercept_bump_wheel_base_change_li+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )

    # Right wheel base change plot
    fig_bump_wheel_base_change.add_trace(go.Scatter(x=df_bump_offset['bump_wheel_travel_re'], 
                                   y=df_bump_offset['bump_wheel_base_re'],
                                   mode='lines+markers', name='Bump wheel_base_change Right'), 
                        row=1, col=2)
    # Regression line for Right wheel_base_change
    fig_bump_wheel_base_change.add_trace(go.Scatter(x=np.linspace(-10, 10, 400), 
                                   y=slope_bump_wheel_base_change_re * np.linspace(-10, 10, 400) + intercept_bump_wheel_base_change_re,
                                   mode='lines', name=f"y={slope_bump_wheel_base_change_re:.4f}x + {intercept_bump_wheel_base_change_re:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=2)
    fig_bump_wheel_base_change.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_wheel_base_change_re:.4f}x + {intercept_bump_wheel_base_change_re:.4f}",
            xref="x2", yref="y2",
            x=0, y=slope_bump_wheel_base_change_re * 0 + intercept_bump_wheel_base_change_re+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )
    
    # Left track change plot
    fig_bump_track_change.add_trace(go.Scatter(x=df_bump_offset['bump_wheel_travel_li'], 
                                   y=-1*df_bump_offset['bump_tire_cp_y_li'],
                                   mode='lines+markers', name='Bump track_change Left'), 
                        row=1, col=1)
    # Regression line for Left track_change
    fig_bump_track_change.add_trace(go.Scatter(x=np.linspace(-10, 10, 400), 
                                   y=slope_bump_track_change_li * np.linspace(-10, 10, 400) + intercept_bump_track_change_li,
                                   mode='lines', name=f"y={slope_bump_track_change_li:.4f}x + {intercept_bump_track_change_li:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=1)
    fig_bump_track_change.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_track_change_li:.4f}x + {intercept_bump_track_change_li:.4f}",
            xref="x1", yref="y1",
            x=0, y=slope_bump_track_change_li * 0 + intercept_bump_track_change_li+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )

    # Right track change plot
    fig_bump_track_change.add_trace(go.Scatter(x=df_bump_offset['bump_wheel_travel_re'], 
                                   y=df_bump_offset['bump_tire_cp_y_re'],
                                   mode='lines+markers', name='Bump track_change Right'), 
                        row=1, col=2)
    # Regression line for Right track_change
    fig_bump_track_change.add_trace(go.Scatter(x=np.linspace(-10, 10, 400), 
                                   y=slope_bump_track_change_re * np.linspace(-10, 10, 400) + intercept_bump_track_change_re,
                                   mode='lines', name=f"y={slope_bump_track_change_re:.4f}x + {intercept_bump_track_change_re:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=2)
    fig_bump_track_change.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_track_change_re:.4f}x + {intercept_bump_track_change_re:.4f}",
            xref="x2", yref="y2",
            x=0, y=slope_bump_track_change_re * 0 + intercept_bump_track_change_re+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )
    
    
    
    # Updating layout for titles, and legend for bump Steer plot
    fig_bump_steer.update_layout(title_text="Steer Offset Plots", width=2400, height=1500,
                            xaxis_title="Rebound <<        RL wheel center vertical travel [mm]        >> Jounce",
                            yaxis_title="toe out <<        RL toe angle variation [deg]        >> toe in",
                            xaxis2_title="Rebound <<        RR wheel center vertical travel [mm]        >> Jounce",
                            yaxis2_title="toe out <<        RR toe angle variation [deg]        >> toe in",
                            showlegend=True)
    
    # Updating layout for titles, and legend for bump Camber plot
    fig_bump_camber.update_layout(title_text="Camber Offset Plots", width=2400, height=1500,
                             xaxis_title="Rebound <<        RL wheel center vertical travel [mm]        >> Jounce",
                             yaxis_title="top in <<        RL toe angle variation [deg]        >> top out",
                             xaxis2_title="Rebound <<        RR wheel center vertical travel [mm]        >> Jounce",
                             yaxis2_title="top in <<        RR toe angle variation [deg]        >> top out",
                             showlegend=True)
    
    
    
    
    
    
    # Update legend names for Steer plot
    for trace in fig_bump_steer.data:
        if trace.name == 'Left Steer':
            trace.name = 'Left'
        elif trace.name == 'Right Steer':
            trace.name = 'Right'

    # Update legend names for Camber plot
    for trace in fig_bump_camber.data:
        if trace.name == 'Left Camber':
            trace.name = 'Left'
        elif trace.name == 'Right Camber':
            trace.name = 'Right'
    
    return (
        fig_bump_wheel_rate, fig_bump_steer, fig_bump_camber, fig_bump_wheel_base_change, fig_bump_track_change, 
        slope_bump_wheel_rate_li, slope_bump_wheel_rate_re, 
        slope_bump_steer_li, slope_bump_steer_re, 
        slope_bump_camber_li, slope_bump_camber_re, 
        slope_bump_wheel_base_change_li, slope_bump_wheel_base_change_re,
        slope_bump_track_change_li, slope_bump_track_change_re
    )
    
    
#    return fig_bump_wheel_rate, fig_bump_steer, fig_bump_camber, fig_bump_wheel_base_change, fig_bump_track_change, slope_li, slope_re, slope_camber_li, slope_camber_re

if __name__ == "__main__":
    main()
