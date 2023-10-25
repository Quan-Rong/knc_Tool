import streamlit as st
import pandas as pd
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import linregress
import numpy as np
from PIL import Image

st.set_page_config(page_title="lat_antiphase", page_icon="📈", layout="wide")

lat_antiphase_image=Image.open('logo_lat_antiphase_01.JPG')
st.image(lat_antiphase_image, caption='Version: Beta V0.2', use_column_width='always')

#程序中，所有的变量都以lat_antiphase_开头用以区分

def main():
    st.title("K&C Test - Lateral Force (Anti-Phase)")
    # Erklärung
    lat_antiphase_description_col1, lat_antiphase_description_col2 = st.columns([3, 1])
        
    with lat_antiphase_description_col1:
        st.markdown("* Body position is fiexed.")
        st.markdown("* Wheel pads are displaced laterally, either in phase across the axle or in opposition.")
        st.markdown("* Wheel pads 'float' (force controlled to zero load) longitudinally and in rotation.")
        st.markdown("* Steering angle is fixed.")
        st.markdown("* Lateral load or displacement limits and cycle time can be specified.")
        st.markdown("* Key results are: **Compliance Steer**, **Compliance Camber**, **Lateral Stiffness**, **Jacking force**, **Roll Centres**")
                   
    with lat_antiphase_description_col2:
        lat_antiphase_image=Image.open('logo_lat_antiphase_02.JPG')
        st.image(lat_antiphase_image, caption='Adams/Car')
        

    lat_antiphase_uploaded_file = st.file_uploader("Choose a .res file", type=[".res"])
    

    if lat_antiphase_uploaded_file:
        lat_antiphase_content = lat_antiphase_uploaded_file.read().decode('utf-8')
        lat_antiphase_blocks = lat_antiphase_extract_blocks(lat_antiphase_content)
        
        if lat_antiphase_blocks:
            lat_antiphase_process_blocks(lat_antiphase_blocks, lat_antiphase_uploaded_file)
        else:
            st.write("No valid data blocks found in the file.")

def lat_antiphase_extract_blocks(lat_antiphase_content):
    lat_antiphase_pattern = r'<Step type="quasiStatic">([\s\S]*?)</Step>'
    lat_antiphase_blocks = re.findall(lat_antiphase_pattern, lat_antiphase_content)
    return lat_antiphase_blocks

def lat_antiphase_process_blocks(lat_antiphase_blocks, lat_antiphase_uploaded_file):
    # Extract values using the provided method
    lat_antiphase_tire_force_y_li = [-1*float(lat_antiphase_block.split()[1097]) for lat_antiphase_block in lat_antiphase_blocks]
    lat_antiphase_tire_force_y_re = [float(lat_antiphase_block.split()[1109]) for lat_antiphase_block in lat_antiphase_blocks]
    #
    lat_antiphase_toe_li = [float(lat_antiphase_block.split()[1025])*180/3.1415926 for lat_antiphase_block in lat_antiphase_blocks]
    lat_antiphase_toe_re = [float(lat_antiphase_block.split()[1026])*180/3.1415926 for lat_antiphase_block in lat_antiphase_blocks]
    #
    lat_antiphase_camber_li = [float(lat_antiphase_block.split()[1027])*180/3.1415926 for lat_antiphase_block in lat_antiphase_blocks]
    lat_antiphase_camber_re = [float(lat_antiphase_block.split()[1028])*180/3.1415926 for lat_antiphase_block in lat_antiphase_blocks]
    #
    lat_antiphase_wc_track_li = [float(lat_antiphase_block.split()[924]) for lat_antiphase_block in lat_antiphase_blocks]
    lat_antiphase_wc_track_re = [-1*float(lat_antiphase_block.split()[925]) for lat_antiphase_block in lat_antiphase_blocks]

    # Create DataFrame
    df_lat_antiphase = pd.DataFrame({
        'lat_antiphase_tire_force_y_li': lat_antiphase_tire_force_y_li,
        'lat_antiphase_tire_force_y_re': lat_antiphase_tire_force_y_re,
        'lat_antiphase_toe_li': lat_antiphase_toe_li,
        'lat_antiphase_toe_re': lat_antiphase_toe_re,
        'lat_antiphase_camber_li': lat_antiphase_camber_li,
        'lat_antiphase_camber_re': lat_antiphase_camber_re,
        'lat_antiphase_wc_track_li': lat_antiphase_wc_track_li,
        'lat_antiphase_wc_track_re': lat_antiphase_wc_track_re,
    })

    # Find the row where lat_antiphase_tire_force_y_li is closest to 0
    offset_row = df_lat_antiphase.iloc[(df_lat_antiphase['lat_antiphase_tire_force_y_li']).abs().idxmin()]
    
    # Subtract the values of this row from the entire DataFrame to create df_lat_antiphase_offset
    df_lat_antiphase_offset = df_lat_antiphase.subtract(offset_row)

    st.write(f"Number of available data blocks = {len(lat_antiphase_blocks)}")
    
    # Display columns in multiselect
    selected_columns = st.multiselect("Select columns:", df_lat_antiphase_offset.columns.tolist(), default=df_lat_antiphase_offset.columns.tolist())

    # Display selected columns from df_lat_antiphase_offset
    if selected_columns:
        st.dataframe(df_lat_antiphase_offset[selected_columns], width= 2400, height= 300)
        st.dataframe(df_lat_antiphase[selected_columns], width= 2400, height= 300)
    
    # Plotting
    if st.button("Plot Graphs (lat_antiphase-Phase Test)"):
        
        #定义要在按下后输出的内容
        (
            fig_lat_antiphase_compliance, fig_lat_antiphase_steer, fig_lat_antiphase_camber,  
            slope_lat_antiphase_compliance_li, slope_lat_antiphase_compliance_re, 
            slope_lat_antiphase_steer_li, slope_lat_antiphase_steer_re, 
            slope_lat_antiphase_camber_li, slope_lat_antiphase_camber_re
        ) = plot_graphs(df_lat_antiphase_offset)
        
        # fig_steer, fig_camber, slope_li, slope_re, slope_camber_li, slope_camber_re = plot_graphs(df_lat_antiphase_offset)
        
        fig_lat_antiphase_compliance.update_layout(title_text="Lateral_Anti-Phase Wheel Center Compliance: [mm/N]", title_font=dict(size=24, family="Arial Bold"), width=1600, height=800)
        fig_lat_antiphase_steer.update_layout(title_text="Lateral_Anti-Phase Steer: [deg/N]", title_font=dict(size=24, family="Arial Bold"), width=1600, height=800)
        fig_lat_antiphase_camber.update_layout(title_text="Lateral_Anti-Phase Camber: [deg/N]", title_font=dict(size=24, family="Arial Bold"), width=1600, height=800)
        
        # Create DataFrame for results
        lat_antiphase_results = pd.DataFrame({
            'Parameter': [
                'lat_antiphase_compliance_li', 'lat_antiphase_compliance_re',
                'lat_antiphase_Toe_Change_li', 'lat_antiphase_Toe_Change_re', 
                'lat_antiphase_Camber_Change_li', 'lat_antiphase_Camber_Change_re'
                ],
            'Slope': [
                slope_lat_antiphase_compliance_li, slope_lat_antiphase_compliance_re,
                slope_lat_antiphase_steer_li, slope_lat_antiphase_steer_re, 
                slope_lat_antiphase_camber_li, slope_lat_antiphase_camber_re
                ]
        })

        # Display the DataFrame in Streamlit
        #st.table(lat_antiphase_results.T.astype(str))
        st.table(lat_antiphase_results.round(5).T.astype(str))
        
        # sidebar display
        st.sidebar.title('Key Results Overview:')
        st.sidebar.markdown('---')
        st.sidebar.table(lat_antiphase_results.iloc[::2].round(5).astype(str))
        if st.sidebar.button('Save CSV'):
            lat_antiphase_results.iloc[::2].to_csv('lat_antiphase_results_odd_rows.csv', index=False)
            st.sidebar.write('File saved as lat_antiphase_results_odd_rows.csv')
        
        # Update layout for fig_lat_antiphase_compliance
        fig_lat_antiphase_compliance.update_layout(
            xaxis_title_font=dict(size=18, family='Arial Bold'), 
            yaxis_title_font=dict(size=18, family='Arial Bold'),
            xaxis_tickfont=dict(size=18, family='Arial Bold'),
            yaxis_tickfont=dict(size=18, family='Arial Bold'),
            legend_font=dict(size=18, family='Arial Bold')
        )
        # Do the same for the second xaxis and yaxis (for the right subplot)
        fig_lat_antiphase_compliance.update_layout(
            xaxis2_title_font=dict(size=18, family='Arial Bold'), 
            yaxis2_title_font=dict(size=18, family='Arial Bold'),
            xaxis2_tickfont=dict(size=18, family='Arial Bold'),
            yaxis2_tickfont=dict(size=18, family='Arial Bold')
        )
        
        # Update layout for fig_lat_antiphase_steer
        fig_lat_antiphase_steer.update_layout(
            xaxis_title_font=dict(size=18, family='Arial Bold'), 
            yaxis_title_font=dict(size=18, family='Arial Bold'),
            xaxis_tickfont=dict(size=18, family='Arial Bold'),
            yaxis_tickfont=dict(size=18, family='Arial Bold'),
            legend_font=dict(size=18, family='Arial Bold')
        )
        # Do the same for the second xaxis and yaxis (for the right subplot)
        fig_lat_antiphase_steer.update_layout(
            xaxis2_title_font=dict(size=18, family='Arial Bold'), 
            yaxis2_title_font=dict(size=18, family='Arial Bold'),
            xaxis2_tickfont=dict(size=18, family='Arial Bold'),
            yaxis2_tickfont=dict(size=18, family='Arial Bold')
        )

        # Update layout for fig_lat_antiphase_camber
        fig_lat_antiphase_camber.update_layout(
            xaxis_title_font=dict(size=18, family='Arial Bold'), 
            yaxis_title_font=dict(size=18, family='Arial Bold'),
            xaxis_tickfont=dict(size=18, family='Arial Bold'),
            yaxis_tickfont=dict(size=18, family='Arial Bold'),
            legend_font=dict(size=18, family='Arial Bold')
        )
        # Do the same for the second xaxis and yaxis (for the right subplot)
        fig_lat_antiphase_camber.update_layout(
            xaxis2_title_font=dict(size=18, family='Arial Bold'), 
            yaxis2_title_font=dict(size=18, family='Arial Bold'),
            xaxis2_tickfont=dict(size=18, family='Arial Bold'),
            yaxis2_tickfont=dict(size=18, family='Arial Bold')
        )
        
        
        # Update background color for fig_lat_antiphase_compliance
        fig_lat_antiphase_compliance.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            xaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray')
        )

        # Update background color for fig_lat_antiphase_steer
        fig_lat_antiphase_steer.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            xaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray')
        )

        # Update background color for fig_lat_antiphase_camber
        fig_lat_antiphase_camber.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            xaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray')
        )
        
        st.markdown('---')
        
        if lat_antiphase_uploaded_file:
            st.write(f"You uploaded: {lat_antiphase_uploaded_file.name}")
            
        st.markdown("* Wheel rate in roll defines the suspension stiffness for single wheel inputs and hence the ride behaviour over rougher road surfaces.")
        st.markdown("* Toral roll stiffness defines the body roll behaviour during cornering.") 
        st.markdown("* Front to rear roll stiffness distribution affects the handling balance. This is most significant in the non-linear handling regime (higher levels of lateral acceleration.)")     
        
        st.plotly_chart(fig_lat_antiphase_compliance)
        
        # Display the regression line equations
        lat_antiphase_compliance_col1, lat_antiphase_compliance_col2, lat_antiphase_compliance_col3 = st.columns([1, 1, 1])
        
        with lat_antiphase_compliance_col1:
            st.markdown("**Curve Fitting Left  (-500 N <-> +500 N ) [mm/kN]:**")
            st.text_input(label="", value=f"{slope_lat_antiphase_compliance_li*1000:.5f}", key="result_display_lat_antiphase_compliance_li") 
                   
        with lat_antiphase_compliance_col2:
            st.markdown("**Curve Fitting Right  (-500 N <-> +500 Nm ) [mm/kN]:**")
            st.text_input(label="", value=f"{slope_lat_antiphase_compliance_re*1000:.5f}", key="result_display_lat_antiphase_compliance_re")
            
        
        
        st.markdown('---')
        if lat_antiphase_uploaded_file:
            st.write(f"You uploaded: {lat_antiphase_uploaded_file.name}")
            
        st.markdown("* Roll steer influences lateral dynamics in term of response gain and response timing. Roll understeer at the front (toe-out during bump) reduces steering sensitivity, but reduces response delay.")
        st.markdown("* Roll understeer at the rear (toe-in during bump) reduces side-slip gain.")
        st.markdown("* Roll understeer is used to improve the linearity of response - the consistency of gain between inputs of different magnitudes.")  
        st.markdown("* The amount of roll steer that occurs in a corner is controlled by the body roll stiffness.")
        
        st.plotly_chart(fig_lat_antiphase_steer)
        
        # Display the regression line equations
        lat_antiphase_steer_col1, lat_antiphase_steer_col2, lat_antiphase_steer_col3 = st.columns([1, 1, 1])
        
        with lat_antiphase_steer_col1:
            st.markdown("**Curve Fitting Left  (-500 N <-> +500 N ) [deg/kN]:**")
            st.text_input(label="", value=f"{slope_lat_antiphase_steer_li * 1000:.5f}", key="result_display_lat_antiphase_steer_li") 
                   
        with lat_antiphase_steer_col2:
            st.markdown("**Curve Fitting Right  (-500 N <-> +500 N ) [deg/kN]:**")
            st.text_input(label="", value=f"{slope_lat_antiphase_steer_re * 1000:.5f}", key="result_display_lat_antiphase_steer_re")
            
        
        
        st.markdown('---')
        if lat_antiphase_uploaded_file:
            st.write(f"You uploaded: {lat_antiphase_uploaded_file.name}")
            
        st.markdown("* Roll camber influences lateral dynamics by affecting tyre slip behaviour and generating camber thrust.")
        st.markdown("* The degree to which a suspension camber the wheel in opposition to the body roll is referred to as camber compensation.")
        st.markdown("* Full camber compensation means the wheel remains at its static level whilst the body rolls. Camber compensation is used to optimise tyre grip.")
        st.markdown("* Front to rear camber compensation ratio influences the handling balance.")
        
        st.plotly_chart(fig_lat_antiphase_camber)
        # Display the regression line equations
        lat_antiphase_camber_col1, lat_antiphase_camber_col2, lat_antiphase_camber_col3 = st.columns([1, 1, 1])
        
        with lat_antiphase_camber_col1:
            st.markdown("**Curve Fitting Left  (-500 N <-> +500 N ) [deg/kN]:**")
            st.text_input(label="", value=f"{slope_lat_antiphase_camber_li * 1000:.5f}", key="result_display_lat_antiphase_camber_li") 
                   
        with lat_antiphase_camber_col2:
            st.markdown("**Curve Fitting Right  (-500 N <-> +500 N ) [deg/kN]:**")
            st.text_input(label="", value=f"{slope_lat_antiphase_camber_re * 1000:.5f}", key="result_display_lat_antiphase_camber_re")

            
            


def plot_graphs(df_lat_antiphase_offset):
    
    # Create the 1. figure with subplots for Steer
    fig_lat_antiphase_compliance = make_subplots(rows=1, cols=2,
                              subplot_titles=('Lateral_Anti-Phase Wheel Center Compliance [mm/N]. Rear Left', 'Lateral_Anti-Phase Wheel Center Compliance [N/mm]. Rear Right'))
    
    # Create the 2. figure with subplots for Steer
    fig_lat_antiphase_steer = make_subplots(rows=1, cols=2,
                              subplot_titles=('Lateral_Anti-Phase Steer [deg/N]. Rear Left', 'Lateral_Anti-Phase Steer [deg/N]. Rear Right'))
    
    # Create the 3. figure with subplots for Camber
    fig_lat_antiphase_camber = make_subplots(rows=1, cols=2,
                               subplot_titles=('Lateral_Anti-Phase Camber [deg/N]. Rear Left', 'Lateral_Anti-Phase Camber [deg/N]. Rear Right'))
    
    
    

    # Filter data for linear regression
    lat_antiphase_offset_mask_li = (df_lat_antiphase_offset['lat_antiphase_tire_force_y_li'] >= -500) & (df_lat_antiphase_offset['lat_antiphase_tire_force_y_li'] <= 500)
    lat_antiphase_offset_mask_re = (df_lat_antiphase_offset['lat_antiphase_tire_force_y_re'] >= -500) & (df_lat_antiphase_offset['lat_antiphase_tire_force_y_re'] <= 500)
    
    # Filter data only for wheel rate linear regression
    # lat_antiphase_mask_li = (df_lat_antiphase['lat_antiphase_tire_force_y_li'] >= -25) & (df_lat_antiphase['lat_antiphase_tire_force_y_li'] <= 25)
    # lat_antiphase_mask_re = (df_lat_antiphase['lat_antiphase_tire_force_y_re'] >= -25) & (df_lat_antiphase['lat_antiphase_tire_force_y_re'] <= 25)    
    
    
    
    # Linear regression for Left compliance
    slope_lat_antiphase_compliance_li, intercept_lat_antiphase_compliance_li, _, _, _ = linregress(df_lat_antiphase_offset[lat_antiphase_offset_mask_li]['lat_antiphase_tire_force_y_li'], 
                                                            df_lat_antiphase_offset[lat_antiphase_offset_mask_li]['lat_antiphase_wc_track_li'])
    # Linear regression for Right compliance
    slope_lat_antiphase_compliance_re, intercept_lat_antiphase_compliance_re, _, _, _ = linregress(df_lat_antiphase_offset[lat_antiphase_offset_mask_re]['lat_antiphase_tire_force_y_re'], 
                                                            df_lat_antiphase_offset[lat_antiphase_offset_mask_re]['lat_antiphase_wc_track_re'])
    
    # Linear regression for Left Steer
    slope_lat_antiphase_steer_li, intercept_lat_antiphase_steer_li, _, _, _ = linregress(df_lat_antiphase_offset[lat_antiphase_offset_mask_li]['lat_antiphase_tire_force_y_li'], 
                                                            df_lat_antiphase_offset[lat_antiphase_offset_mask_li]['lat_antiphase_toe_li'])
    # Linear regression for Right Steer
    slope_lat_antiphase_steer_re, intercept_lat_antiphase_steer_re, _, _, _ = linregress(df_lat_antiphase_offset[lat_antiphase_offset_mask_re]['lat_antiphase_tire_force_y_re'], 
                                                            df_lat_antiphase_offset[lat_antiphase_offset_mask_re]['lat_antiphase_toe_re'])
    
    # Linear regression for Left Camber
    slope_lat_antiphase_camber_li, intercept_lat_antiphase_camber_li, _, _, _ = linregress(df_lat_antiphase_offset[lat_antiphase_offset_mask_li]['lat_antiphase_tire_force_y_li'], 
                                                              df_lat_antiphase_offset[lat_antiphase_offset_mask_li]['lat_antiphase_camber_li'])
    # Linear regression for Right Camber
    slope_lat_antiphase_camber_re, intercept_lat_antiphase_camber_re, _, _, _ = linregress(df_lat_antiphase_offset[lat_antiphase_offset_mask_re]['lat_antiphase_tire_force_y_re'], 
                                                              df_lat_antiphase_offset[lat_antiphase_offset_mask_re]['lat_antiphase_camber_re'])
    
    
    # Left compliance plot
    # 由于数据点太多，所以每隔10个显示一个点，所以进行提取
    fig_lat_antiphase_compliance.add_trace(go.Scatter(x=df_lat_antiphase_offset['lat_antiphase_tire_force_y_li'][::10], 
                                   y=df_lat_antiphase_offset['lat_antiphase_wc_track_li'][::10],
                                   mode='lines+markers', name='Lateral_Anti-Phase @WC Comp. Left',
                                   line=dict(
                                        width=2,  # line width
                                        color='rgba(255, 165, 0, 1)'  # line color
                                        ),
                                   marker=dict(
                                        size=5,
                                        color='white',
                                        line=dict(
                                        width=1,  # 设置外围线的宽度
                                        color='rgba(0, 0, 0, 1)'  # 设置外围线的颜色
                                        )
                                   )    
                                   ), 
                        row=1, col=1) 
    # Regression line for Left Steer
    fig_lat_antiphase_compliance.add_trace(go.Scatter(x=np.linspace(-500, 500, 400), 
                                   y=slope_lat_antiphase_compliance_li * np.linspace(-500, 500, 400) + intercept_lat_antiphase_compliance_li,
                                   mode='lines', name=f"y={slope_lat_antiphase_compliance_li:.5f}x + {intercept_lat_antiphase_compliance_li:.5f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=1)
    fig_lat_antiphase_compliance.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_lat_antiphase_compliance_li:.5f}x + {intercept_lat_antiphase_compliance_li:.5f}",
            xref="x1", yref="y1",
            x=0, y=slope_lat_antiphase_compliance_li * 0 + intercept_lat_antiphase_compliance_li+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )

    # Right compliance plot
    # 由于数据点太多，所以每隔10个显示一个点，所以进行提取
    fig_lat_antiphase_compliance.add_trace(go.Scatter(x=df_lat_antiphase_offset['lat_antiphase_tire_force_y_re'][::10], 
                                   y=df_lat_antiphase_offset['lat_antiphase_wc_track_re'][::10],
                                   mode='lines+markers', name='Lateral_Anti-Phase @WC Comp. Right',
                                   line=dict(
                                        width=2,  # line width
                                        color='rgba(255, 165, 0, 1)'  # line color
                                        ),
                                   marker=dict(
                                        size=5,
                                        color='white',
                                        line=dict(
                                        width=1,  # 设置外围线的宽度
                                        color='rgba(0, 0, 0, 1)'  # 设置外围线的颜色
                                        )
                                   )    
                                   ), 
                        row=1, col=2) 
    # Regression line for Right Steer
    fig_lat_antiphase_compliance.add_trace(go.Scatter(x=np.linspace(-500, 500, 400), 
                                   y=slope_lat_antiphase_compliance_re * np.linspace(-500, 500, 400) + intercept_lat_antiphase_compliance_re,
                                   mode='lines', name=f"y={slope_lat_antiphase_compliance_re:.5f}x + {intercept_lat_antiphase_compliance_re:.5f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=2)
    fig_lat_antiphase_compliance.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_lat_antiphase_compliance_re:.5f}x + {intercept_lat_antiphase_compliance_re:.5f}",
            xref="x2", yref="y2",
            x=0, y=slope_lat_antiphase_compliance_re * 0 + intercept_lat_antiphase_compliance_re+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )    
    
    # Left Steer plot
    # 由于数据点太多，所以每隔10个显示一个点，所以进行提取
    
    fig_lat_antiphase_steer.add_trace(go.Scatter(x=df_lat_antiphase_offset['lat_antiphase_tire_force_y_li'][::10], 
                                   y=df_lat_antiphase_offset['lat_antiphase_toe_li'][::10],
                                   mode='lines+markers', name='Lateral_Anti-Phase Steer Left', 
                                   line=dict(
                                        width=2,  # line width
                                        color='rgba(255, 165, 0, 1)'  # line color
                                        ),
                                   marker=dict(
                                        size=5,
                                        color='white',
                                        line=dict(
                                        width=1,  # 设置外围线的宽度
                                        color='rgba(0, 0, 0, 1)'  # 设置外围线的颜色
                                        )
                                   )    
                                   ), 
                        row=1, col=1)
    # Regression line for Left Steer
    fig_lat_antiphase_steer.add_trace(go.Scatter(x=np.linspace(-500, 500, 400), 
                                   y=slope_lat_antiphase_steer_li * np.linspace(-500, 500, 400) + intercept_lat_antiphase_steer_li,
                                   mode='lines', name=f"y={slope_lat_antiphase_steer_li:.5f}x + {intercept_lat_antiphase_steer_li:.5f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=1)
    fig_lat_antiphase_steer.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_lat_antiphase_steer_li:.5f}x + {intercept_lat_antiphase_steer_li:.5f}",
            xref="x1", yref="y1",
            x=0, y=slope_lat_antiphase_steer_li * 0 + intercept_lat_antiphase_steer_li+0.1,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )

    # Right Steer plot
    # 由于数据点太多，所以每隔10个显示一个点，所以进行提取
    fig_lat_antiphase_steer.add_trace(go.Scatter(x=df_lat_antiphase_offset['lat_antiphase_tire_force_y_re'][::10], 
                                   y=df_lat_antiphase_offset['lat_antiphase_toe_re'][::10],
                                   mode='lines+markers', name='Lateral_Anti-Phase Steer Right', 
                                   line=dict(
                                        width=2,  # line width
                                        color='rgba(255, 165, 0, 1)'  # line color
                                        ),
                                   marker=dict(
                                        size=5,
                                        color='white',
                                        line=dict(
                                        width=1,  # 设置外围线的宽度
                                        color='rgba(0, 0, 0, 1)'  # 设置外围线的颜色
                                        )
                                   )    
                                   ), 
                        row=1, col=2)
    # Regression line for Right Steer
    fig_lat_antiphase_steer.add_trace(go.Scatter(x=np.linspace(-500, 500, 400), 
                                   y=slope_lat_antiphase_steer_re * np.linspace(-500, 500, 400) + intercept_lat_antiphase_steer_re,
                                   mode='lines', name=f"y={slope_lat_antiphase_steer_re:.5f}x + {intercept_lat_antiphase_steer_re:.5f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=2)
    fig_lat_antiphase_steer.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_lat_antiphase_steer_re:.5f}x + {intercept_lat_antiphase_steer_re:.5f}",
            xref="x2", yref="y2",
            x=0, y=slope_lat_antiphase_steer_re * 0 + intercept_lat_antiphase_steer_re+0.1,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )
    
    # Left Camber plot
    # 由于数据点太多，所以每隔10个显示一个点，所以进行提取
    fig_lat_antiphase_camber.add_trace(go.Scatter(x=df_lat_antiphase_offset['lat_antiphase_tire_force_y_li'][::10], 
                                   y=df_lat_antiphase_offset['lat_antiphase_camber_li'][::10],
                                   mode='lines+markers', name='Lateral_Anti-Phase Camber Left',
                                   line=dict(
                                        width=2,  # line width
                                        color='rgba(255, 165, 0, 1)'  # line color
                                        ),
                                   marker=dict(
                                        size=5,
                                        color='white',
                                        line=dict(
                                        width=1,  # 设置外围线的宽度
                                        color='rgba(0, 0, 0, 1)'  # 设置外围线的颜色
                                        )
                                   )    
                                   ), 
                        row=1, col=1)
    # Regression line for Left Camber
    fig_lat_antiphase_camber.add_trace(go.Scatter(x=np.linspace(-500, 500, 400), 
                                   y=slope_lat_antiphase_camber_li * np.linspace(-500, 500, 400) + intercept_lat_antiphase_camber_li,
                                   mode='lines', name=f"y={slope_lat_antiphase_camber_li:.5f}x + {intercept_lat_antiphase_camber_li:.5f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=1)
    fig_lat_antiphase_camber.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_lat_antiphase_camber_li:.5f}x + {intercept_lat_antiphase_camber_li:.5f}",
            xref="x1", yref="y1",
            x=0, y=slope_lat_antiphase_camber_li * 0 + intercept_lat_antiphase_camber_li+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )

    # Right Camber plot
    # 由于数据点太多，所以每隔10个显示一个点，所以进行提取
    fig_lat_antiphase_camber.add_trace(go.Scatter(x=df_lat_antiphase_offset['lat_antiphase_tire_force_y_re'][::10], 
                                   y=df_lat_antiphase_offset['lat_antiphase_camber_re'][::10],
                                   mode='lines+markers', name='Lateral_Anti-Phase Camber Right',
                                   line=dict(
                                        width=2,  # 设置线的宽度
                                        color='rgba(255, 165, 0, 1)'  # 设置线的颜色
                                        ),
                                   marker=dict(
                                        size=5,
                                        color='white',
                                        line=dict(
                                        width=1,  # 设置外围线的宽度
                                        color='rgba(0, 0, 0, 1)'  # 设置外围线的颜色
                                        )
                                   )    
                                   ), 
                        row=1, col=2)
    # Regression line for Right Camber
    fig_lat_antiphase_camber.add_trace(go.Scatter(x=np.linspace(-500, 500, 400), 
                                   y=slope_lat_antiphase_camber_re * np.linspace(-500, 500, 400) + intercept_lat_antiphase_camber_re,
                                   mode='lines', name=f"y={slope_lat_antiphase_camber_re:.5f}x + {intercept_lat_antiphase_camber_re:.5f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=2)
    fig_lat_antiphase_camber.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_lat_antiphase_camber_re:.5f}x + {intercept_lat_antiphase_camber_re:.5f}",
            xref="x2", yref="y2",
            x=0, y=slope_lat_antiphase_camber_re * 0 + intercept_lat_antiphase_camber_re+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )

    # Updating layout for titles, and legend for lat_antiphase Swheel rate plot
    fig_lat_antiphase_compliance.update_layout(title_text="Compliance Offset Plots", width=2400, height=1500,
                            xaxis_title="Load outward <<        RL lateral force [N]        >> Load inward",
                            yaxis_title="Outward <<        RL lateral displacement @WC [mm]        >> Inward",
                            xaxis2_title="Load outward <<        RL lateral force [N]        >> Load inward",
                            yaxis2_title="Outward <<        RL lateral displacement @WC [mm]        >> Inward",
                            showlegend=True)    
    
    
    # Updating layout for titles, and legend for lat_antiphase Steer plot
    fig_lat_antiphase_steer.update_layout(title_text="Steer Offset Plots", width=2400, height=1500,
                            xaxis_title="Load outward <<        RL lateral force [N]        >> Load inward",
                            yaxis_title="toe out <<        RL toe angle variation [deg]        >> toe in",
                            xaxis2_title="Load outward <<        RL lateral force [N]        >> Load inward",
                            yaxis2_title="toe out <<        RR toe angle variation [deg]        >> toe in",
                            showlegend=True)
    
    # Updating layout for titles, and legend for lat_antiphase Camber plot
    fig_lat_antiphase_camber.update_layout(title_text="Camber Offset Plots", width=2400, height=1500,
                             xaxis_title="Load outward <<        RL lateral force [N]        >> Load inward",
                             yaxis_title="top in <<        RL camber angle variation [deg]        >> top out",
                             xaxis2_title="Load outward <<        RL lateral force [N]        >> Load inward",
                             yaxis2_title="top in <<        RR camber angle variation [deg]        >> top out",
                             showlegend=True)
    
    
    
    
    
    
    # Update legend names for Steer plot
    for trace in fig_lat_antiphase_steer.data:
        if trace.name == 'Left Steer':
            trace.name = 'Left'
        elif trace.name == 'Right Steer':
            trace.name = 'Right'

    # Update legend names for Camber plot
    for trace in fig_lat_antiphase_camber.data:
        if trace.name == 'Left Camber':
            trace.name = 'Left'
        elif trace.name == 'Right Camber':
            trace.name = 'Right'
    
    return (
        fig_lat_antiphase_compliance, fig_lat_antiphase_steer, fig_lat_antiphase_camber, 
        slope_lat_antiphase_compliance_li, slope_lat_antiphase_compliance_re, 
        slope_lat_antiphase_steer_li, slope_lat_antiphase_steer_re, 
        slope_lat_antiphase_camber_li, slope_lat_antiphase_camber_re, 
    )
    
    
#    return fig_lat_antiphase_compliance, fig_lat_antiphase_steer, fig_lat_antiphase_camber, fig_lat_antiphase_wheel_base_change, fig_lat_antiphase_track_change, slope_li, slope_re, slope_camber_li, slope_camber_re

if __name__ == "__main__":
    main()
