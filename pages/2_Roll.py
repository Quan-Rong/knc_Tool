import streamlit as st
import pandas as pd
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import linregress
import numpy as np
from PIL import Image

st.set_page_config(page_title="🎭GESTAMP Static Loads", page_icon="📈", layout="wide")

bump_anti_image=Image.open('logo_bump_anti_01.JPG')
st.image(bump_anti_image, caption='Version: Beta V0.2', use_column_width='always')

#程序中，所有的变量都以bump_anti_开头用以区分

def main():
    st.title("K&C Test - Body Roll (PE: Bump Anti-Phase)")
    # Erklärung
    bump_anti_description_col1, bump_anti_description_col2 = st.columns([3, 1])
        
    with bump_anti_description_col1:
        st.markdown("* Body is rolled whilst controlled in bounce and pitch to ensure constant axle loads.")
        st.markdown("* Wheel pads 'float' (force controlled to zero load) horizontally and in rotation")
        st.markdown("* Steering angle is fixed")
        st.markdown("* Roll angle limits and cycle time can be specified")
        st.markdown("* Key results are: **Roll Stiffness**, **Roll Stiffness Distribution**, **Roll Steer**, **Roll Camber**, **Roll Centre Locations**")
                   
    with bump_anti_description_col2:
        bump_anti_image=Image.open('logo_bump_anti_02.JPG')
        st.image(bump_anti_image, caption='Adams/Car')
        

    bump_anti_uploaded_file = st.file_uploader("Choose a .res file", type=[".res"])
    

    if bump_anti_uploaded_file:
        bump_anti_content = bump_anti_uploaded_file.read().decode('utf-8')
        bump_anti_blocks = bump_anti_extract_blocks(bump_anti_content)
        
        if bump_anti_blocks:
            bump_anti_process_blocks(bump_anti_blocks, bump_anti_uploaded_file)
        else:
            st.write("No valid data blocks found in the file.")

def bump_anti_extract_blocks(bump_anti_content):
    bump_anti_pattern = r'<Step type="quasiStatic">([\s\S]*?)</Step>'
    bump_anti_blocks = re.findall(bump_anti_pattern, bump_anti_content)
    return bump_anti_blocks

def bump_anti_process_blocks(bump_anti_blocks, bump_anti_uploaded_file):
    # Extract values using the provided method
    bump_anti_wheel_travel_li = [float(bump_anti_block.split()[918]) for bump_anti_block in bump_anti_blocks]
    bump_anti_wheel_travel_re = [float(bump_anti_block.split()[919]) for bump_anti_block in bump_anti_blocks]
    #
    bump_anti_toe_li = [float(bump_anti_block.split()[1025])*180/3.1415926 for bump_anti_block in bump_anti_blocks]
    bump_anti_toe_re = [float(bump_anti_block.split()[1026])*180/3.1415926 for bump_anti_block in bump_anti_blocks]
    #
    bump_anti_camber_li = [float(bump_anti_block.split()[1027])*180/3.1415926 for bump_anti_block in bump_anti_blocks]
    bump_anti_camber_re = [float(bump_anti_block.split()[1028])*180/3.1415926 for bump_anti_block in bump_anti_blocks]
    #
    bump_anti_vertical_force_li = [float(bump_anti_block.split()[934]) for bump_anti_block in bump_anti_blocks]
    bump_anti_vertical_force_re = [float(bump_anti_block.split()[935]) for bump_anti_block in bump_anti_blocks]

    # Create DataFrame
    df_bump_anti = pd.DataFrame({
        'bump_anti_wheel_travel_li': bump_anti_wheel_travel_li,
        'bump_anti_wheel_travel_re': bump_anti_wheel_travel_re,
        'bump_anti_toe_li': bump_anti_toe_li,
        'bump_anti_toe_re': bump_anti_toe_re,
        'bump_anti_camber_li': bump_anti_camber_li,
        'bump_anti_camber_re': bump_anti_camber_re,
        'bump_anti_vertical_force_li': bump_anti_vertical_force_li,
        'bump_anti_vertical_force_re': bump_anti_vertical_force_re,
    })

    # Find the row where bump_anti_wheel_travel_li is closest to 0
    offset_row = df_bump_anti.iloc[(df_bump_anti['bump_anti_wheel_travel_li']).abs().idxmin()]
    
    # Subtract the values of this row from the entire DataFrame to create df_bump_anti_offset
    df_bump_anti_offset = df_bump_anti.subtract(offset_row)

    st.write(f"Number of available data blocks = {len(bump_anti_blocks)}")
    
    # Display columns in multiselect
    selected_columns = st.multiselect("Select columns:", df_bump_anti_offset.columns.tolist(), default=df_bump_anti_offset.columns.tolist())

    # Display selected columns from df_bump_anti_offset
    if selected_columns:
        st.dataframe(df_bump_anti_offset[selected_columns], width= 2400, height= 300)
        st.dataframe(df_bump_anti[selected_columns], width= 2400, height= 300)
    
    # Plotting
    if st.button("Plot Graphs (bump_Anti-Phase Test)"):
        
        #定义要在按下后输出的内容
        (
            fig_bump_anti_wheel_rate, fig_bump_anti_steer, fig_bump_anti_camber,  
            slope_bump_anti_wheel_rate_li, slope_bump_anti_wheel_rate_re, 
            slope_bump_anti_steer_li, slope_bump_anti_steer_re, 
            slope_bump_anti_camber_li, slope_bump_anti_camber_re
        ) = plot_graphs(df_bump_anti_offset, df_bump_anti)
        
        # fig_steer, fig_camber, slope_li, slope_re, slope_camber_li, slope_camber_re = plot_graphs(df_bump_anti_offset)
        
        fig_bump_anti_wheel_rate.update_layout(title_text="Bump_Anti-Phase Wheel Rate: [N/mm]", title_font=dict(size=24, family="Arial Bold"), width=1600, height=800)
        fig_bump_anti_steer.update_layout(title_text="Bump_Anti-Phase Steer: [deg/mm]", title_font=dict(size=24, family="Arial Bold"), width=1600, height=800)
        fig_bump_anti_camber.update_layout(title_text="Bump_Anti-Phase Camber: [deg/mm]", title_font=dict(size=24, family="Arial Bold"), width=1600, height=800)
        
        # Create DataFrame for results
        bump_anti_results = pd.DataFrame({
            'Parameter': [
                'bump_anti_Wheel_Rate_li', 'bump_anti_Wheel_Rate_re',
                'bump_anti_Toe_Change_li', 'bump_anti_Toe_Change_re', 
                'bump_anti_Camber_Change_li', 'bump_anti_Camber_Change_re'
                ],
            'Slope': [
                slope_bump_anti_wheel_rate_li, slope_bump_anti_wheel_rate_re,
                slope_bump_anti_steer_li, slope_bump_anti_steer_re, 
                slope_bump_anti_camber_li, slope_bump_anti_camber_re
                ]
        })

        # Display the DataFrame in Streamlit
        #st.table(bump_anti_results.T.astype(str))
        st.table(bump_anti_results.round(4).T.astype(str))
        
        # sidebar display
        st.sidebar.title('Key Results Overview:')
        st.sidebar.markdown('---')
        st.sidebar.table(bump_anti_results.iloc[::2].round(4).astype(str))
        if st.sidebar.button('Save CSV'):
            bump_anti_results.iloc[::2].to_csv('bump_anti_results_odd_rows.csv', index=False)
            st.sidebar.write('File saved as bump_anti_results_odd_rows.csv')
        
        # Update layout for fig_bump_anti_wheel_rate
        fig_bump_anti_wheel_rate.update_layout(
            xaxis_title_font=dict(size=18, family='Arial Bold'), 
            yaxis_title_font=dict(size=18, family='Arial Bold'),
            xaxis_tickfont=dict(size=18, family='Arial Bold'),
            yaxis_tickfont=dict(size=18, family='Arial Bold'),
            legend_font=dict(size=18, family='Arial Bold')
        )
        # Do the same for the second xaxis and yaxis (for the right subplot)
        fig_bump_anti_wheel_rate.update_layout(
            xaxis2_title_font=dict(size=18, family='Arial Bold'), 
            yaxis2_title_font=dict(size=18, family='Arial Bold'),
            xaxis2_tickfont=dict(size=18, family='Arial Bold'),
            yaxis2_tickfont=dict(size=18, family='Arial Bold')
        )
        
        # Update layout for fig_bump_anti_steer
        fig_bump_anti_steer.update_layout(
            xaxis_title_font=dict(size=18, family='Arial Bold'), 
            yaxis_title_font=dict(size=18, family='Arial Bold'),
            xaxis_tickfont=dict(size=18, family='Arial Bold'),
            yaxis_tickfont=dict(size=18, family='Arial Bold'),
            legend_font=dict(size=18, family='Arial Bold')
        )
        # Do the same for the second xaxis and yaxis (for the right subplot)
        fig_bump_anti_steer.update_layout(
            xaxis2_title_font=dict(size=18, family='Arial Bold'), 
            yaxis2_title_font=dict(size=18, family='Arial Bold'),
            xaxis2_tickfont=dict(size=18, family='Arial Bold'),
            yaxis2_tickfont=dict(size=18, family='Arial Bold')
        )

        # Update layout for fig_bump_anti_camber
        fig_bump_anti_camber.update_layout(
            xaxis_title_font=dict(size=18, family='Arial Bold'), 
            yaxis_title_font=dict(size=18, family='Arial Bold'),
            xaxis_tickfont=dict(size=18, family='Arial Bold'),
            yaxis_tickfont=dict(size=18, family='Arial Bold'),
            legend_font=dict(size=18, family='Arial Bold')
        )
        # Do the same for the second xaxis and yaxis (for the right subplot)
        fig_bump_anti_camber.update_layout(
            xaxis2_title_font=dict(size=18, family='Arial Bold'), 
            yaxis2_title_font=dict(size=18, family='Arial Bold'),
            xaxis2_tickfont=dict(size=18, family='Arial Bold'),
            yaxis2_tickfont=dict(size=18, family='Arial Bold')
        )
        
        
        # Update background color for fig_bump_anti_wheel_rate
        fig_bump_anti_wheel_rate.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            xaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray')
        )

        # Update background color for fig_bump_anti_steer
        fig_bump_anti_steer.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            xaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray')
        )

        # Update background color for fig_bump_anti_camber
        fig_bump_anti_camber.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            xaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray'),
            yaxis2=dict(gridcolor='lightgray',zerolinecolor='lightgray')
        )
        
        st.markdown('---')
        
        if bump_anti_uploaded_file:
            st.write(f"You uploaded: {bump_anti_uploaded_file.name}")
            
        st.markdown("* Wheel rate in roll defines the suspension stiffness for single wheel inputs and hence the ride behaviour over rougher road surfaces.")
        st.markdown("* Toral roll stiffness defines the body roll behaviour during cornering.") 
        st.markdown("* Front to rear roll stiffness distribution affects the handling balance. This is most significant in the non-linear handling regime (higher levels of lateral acceleration.)")     
        
        st.plotly_chart(fig_bump_anti_wheel_rate)
        
        # Display the regression line equations
        bump_anti_wheel_rate_col1, bump_anti_wheel_rate_col2, bump_anti_wheel_rate_col3 = st.columns([1, 1, 1])
        
        with bump_anti_wheel_rate_col1:
            st.markdown("**Curve Fitting Left  (-25mm <-> +25mm ) [N/mm]:**")
            st.text_input(label="", value=f"{slope_bump_anti_wheel_rate_li:.4f}", key="result_display_bump_anti_wheel_rate_li") 
                   
        with bump_anti_wheel_rate_col2:
            st.markdown("**Curve Fitting Right  (-25mm <-> +25mm ) [N/mm]:**")
            st.text_input(label="", value=f"{slope_bump_anti_wheel_rate_re:.4f}", key="result_display_bump_anti_wheel_rate_re")
            
        
        
        st.markdown('---')
        if bump_anti_uploaded_file:
            st.write(f"You uploaded: {bump_anti_uploaded_file.name}")
            
        st.markdown("* Roll steer influences lateral dynamics in term of response gain and response timing. Roll understeer at the front (toe-out during bump) reduces steering sensitivity, but reduces response delay.")
        st.markdown("* Roll understeer at the rear (toe-in during bump) reduces side-slip gain.")
        st.markdown("* Roll understeer is used to improve the linearity of response - the consistency of gain between inputs of different magnitudes.")  
        st.markdown("* The amount of roll steer that occurs in a corner is controlled by the body roll stiffness.")
        
        st.plotly_chart(fig_bump_anti_steer)
        
        # Display the regression line equations
        bump_anti_steer_col1, bump_anti_steer_col2, bump_anti_steer_col3 = st.columns([1, 1, 1])
        
        with bump_anti_steer_col1:
            st.markdown("**Curve Fitting Left  (-25mm <-> +25mm ) [deg/m]:**")
            st.text_input(label="", value=f"{slope_bump_anti_steer_li * 1000:.4f}", key="result_display_bump_anti_steer_li") 
                   
        with bump_anti_steer_col2:
            st.markdown("**Curve Fitting Right  (-25mm <-> +25mm ) [deg/m]:**")
            st.text_input(label="", value=f"{slope_bump_anti_steer_re * 1000:.4f}", key="result_display_bump_anti_steer_re")
            
        
        
        st.markdown('---')
        if bump_anti_uploaded_file:
            st.write(f"You uploaded: {bump_anti_uploaded_file.name}")
            
        st.markdown("* Roll camber influences lateral dynamics by affecting tyre slip behaviour and generating camber thrust.")
        st.markdown("* The degree to which a suspension camber the wheel in opposition to the body roll is referred to as camber compensation.")
        st.markdown("* Full camber compensation means the wheel remains at its static level whilst the body rolls. Camber compensation is used to optimise tyre grip.")
        st.markdown("* Front to rear camber compensation ratio influences the handling balance.")
        
        st.plotly_chart(fig_bump_anti_camber)
        # Display the regression line equations
        bump_anti_camber_col1, bump_anti_camber_col2, bump_anti_camber_col3 = st.columns([1, 1, 1])
        
        with bump_anti_camber_col1:
            st.markdown("**Curve Fitting Left  (-25mm <-> +25mm ) [deg/m]:**")
            st.text_input(label="", value=f"{slope_bump_anti_camber_li * 1000:.4f}", key="result_display_bump_anti_camber_li") 
                   
        with bump_anti_camber_col2:
            st.markdown("**Curve Fitting Right  (-25mm <-> +25mm ) [deg/m]:**")
            st.text_input(label="", value=f"{slope_bump_anti_camber_re * 1000:.4f}", key="result_display_bump_anti_camber_re")

            
            


def plot_graphs(df_bump_anti_offset, df_bump_anti):
    
    # Create the 1. figure with subplots for Steer
    fig_bump_anti_wheel_rate = make_subplots(rows=1, cols=2,
                              subplot_titles=('Bump_Anti-Phase Wheel Rate [N/mm]. Rear Left', 'Bump_Anti-Phase Wheel Rate [N/mm]. Rear Right'))
    
    # Create the 2. figure with subplots for Steer
    fig_bump_anti_steer = make_subplots(rows=1, cols=2,
                              subplot_titles=('Bump_Anti-Phase Steer [deg/mm]. Rear Left', 'Bump_Anti-Phase Steer [deg/mm]. Rear Right'))
    
    # Create the 3. figure with subplots for Camber
    fig_bump_anti_camber = make_subplots(rows=1, cols=2,
                               subplot_titles=('Bump_Anti-Phase Camber [deg/mm]. Rear Left', 'Bump_Anti-Phase Camber [deg/mm]. Rear Right'))
    
    
    

    # Filter data for linear regression
    bump_anti_offset_mask_li = (df_bump_anti_offset['bump_anti_wheel_travel_li'] >= -25) & (df_bump_anti_offset['bump_anti_wheel_travel_li'] <= 25)
    bump_anti_offset_mask_re = (df_bump_anti_offset['bump_anti_wheel_travel_re'] >= -25) & (df_bump_anti_offset['bump_anti_wheel_travel_re'] <= 25)
    
    # Filter data only for wheel rate linear regression
    bump_anti_mask_li = (df_bump_anti['bump_anti_wheel_travel_li'] >= -25) & (df_bump_anti['bump_anti_wheel_travel_li'] <= 25)
    bump_anti_mask_re = (df_bump_anti['bump_anti_wheel_travel_re'] >= -25) & (df_bump_anti['bump_anti_wheel_travel_re'] <= 25)    
    
    
    
    # Linear regression for Left wheel_rate
    slope_bump_anti_wheel_rate_li, intercept_bump_anti_wheel_rate_li, _, _, _ = linregress(df_bump_anti[bump_anti_mask_li]['bump_anti_wheel_travel_li'], 
                                                            df_bump_anti[bump_anti_mask_li]['bump_anti_vertical_force_li'])
    # Linear regression for Right wheel_rate
    slope_bump_anti_wheel_rate_re, intercept_bump_anti_wheel_rate_re, _, _, _ = linregress(df_bump_anti[bump_anti_mask_re]['bump_anti_wheel_travel_re'], 
                                                            df_bump_anti[bump_anti_mask_re]['bump_anti_vertical_force_re'])
    
    # Linear regression for Left Steer
    slope_bump_anti_steer_li, intercept_bump_anti_steer_li, _, _, _ = linregress(df_bump_anti_offset[bump_anti_offset_mask_li]['bump_anti_wheel_travel_li'], 
                                                            df_bump_anti_offset[bump_anti_offset_mask_li]['bump_anti_toe_li'])
    # Linear regression for Right Steer
    slope_bump_anti_steer_re, intercept_bump_anti_steer_re, _, _, _ = linregress(df_bump_anti_offset[bump_anti_offset_mask_re]['bump_anti_wheel_travel_re'], 
                                                            df_bump_anti_offset[bump_anti_offset_mask_re]['bump_anti_toe_re'])
    
    # Linear regression for Left Camber
    slope_bump_anti_camber_li, intercept_bump_anti_camber_li, _, _, _ = linregress(df_bump_anti_offset[bump_anti_offset_mask_li]['bump_anti_wheel_travel_li'], 
                                                              df_bump_anti_offset[bump_anti_offset_mask_li]['bump_anti_camber_li'])
    # Linear regression for Right Camber
    slope_bump_anti_camber_re, intercept_bump_anti_camber_re, _, _, _ = linregress(df_bump_anti_offset[bump_anti_offset_mask_re]['bump_anti_wheel_travel_re'], 
                                                              df_bump_anti_offset[bump_anti_offset_mask_re]['bump_anti_camber_re'])
    
    
    # Left wheel rate plot
    fig_bump_anti_wheel_rate.add_trace(go.Scatter(x=df_bump_anti['bump_anti_wheel_travel_li'], 
                                   y=df_bump_anti['bump_anti_vertical_force_li'],
                                   mode='lines+markers', name='Bump Anti-Phase Wheel Rate Left'), 
                        row=1, col=1)
    # Regression line for Left Steer
    fig_bump_anti_wheel_rate.add_trace(go.Scatter(x=np.linspace(-25, 25, 400), 
                                   y=slope_bump_anti_wheel_rate_li * np.linspace(-25, 25, 400) + intercept_bump_anti_wheel_rate_li,
                                   mode='lines', name=f"y={slope_bump_anti_wheel_rate_li:.4f}x + {intercept_bump_anti_wheel_rate_li:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=1)
    fig_bump_anti_wheel_rate.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_anti_wheel_rate_li:.4f}x + {intercept_bump_anti_wheel_rate_li:.4f}",
            xref="x1", yref="y1",
            x=0, y=slope_bump_anti_wheel_rate_li * 0 + intercept_bump_anti_wheel_rate_li+2000,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )

    # Right wheel rate plot
    fig_bump_anti_wheel_rate.add_trace(go.Scatter(x=df_bump_anti['bump_anti_wheel_travel_re'], 
                                   y=df_bump_anti['bump_anti_vertical_force_re'],
                                   mode='lines+markers', name='Bump Anti-Phase Wheel Rate Right'), 
                        row=1, col=2)
    # Regression line for Right Steer
    fig_bump_anti_wheel_rate.add_trace(go.Scatter(x=np.linspace(-25, 25, 400), 
                                   y=slope_bump_anti_wheel_rate_re * np.linspace(-25, 25, 400) + intercept_bump_anti_wheel_rate_re,
                                   mode='lines', name=f"y={slope_bump_anti_wheel_rate_re:.4f}x + {intercept_bump_anti_wheel_rate_re:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=2)
    fig_bump_anti_wheel_rate.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_anti_wheel_rate_re:.4f}x + {intercept_bump_anti_wheel_rate_re:.4f}",
            xref="x2", yref="y2",
            x=0, y=slope_bump_anti_wheel_rate_re * 0 + intercept_bump_anti_wheel_rate_re+2000,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )    
    
    # Left Steer plot
    fig_bump_anti_steer.add_trace(go.Scatter(x=df_bump_anti_offset['bump_anti_wheel_travel_li'], 
                                   y=df_bump_anti_offset['bump_anti_toe_li'],
                                   mode='lines+markers', name='Bump Anti-Phase Steer Left', 
                                   line=dict(
                                        width=2,  # line width
                                        color='rgba(0, 0, 255, 1)'  # line color
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
    fig_bump_anti_steer.add_trace(go.Scatter(x=np.linspace(-25, 25, 400), 
                                   y=slope_bump_anti_steer_li * np.linspace(-25, 25, 400) + intercept_bump_anti_steer_li,
                                   mode='lines', name=f"y={slope_bump_anti_steer_li:.4f}x + {intercept_bump_anti_steer_li:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=1)
    fig_bump_anti_steer.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_anti_steer_li:.4f}x + {intercept_bump_anti_steer_li:.4f}",
            xref="x1", yref="y1",
            x=0, y=slope_bump_anti_steer_li * 0 + intercept_bump_anti_steer_li+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )

    # Right Steer plot
    fig_bump_anti_steer.add_trace(go.Scatter(x=df_bump_anti_offset['bump_anti_wheel_travel_re'], 
                                   y=df_bump_anti_offset['bump_anti_toe_re'],
                                   mode='lines+markers', name='Bump Anti-Phase Steer Right', 
                                   line=dict(
                                        width=2,  # line width
                                        color='rgba(0, 0, 255, 1)'  # line color
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
    fig_bump_anti_steer.add_trace(go.Scatter(x=np.linspace(-25, 25, 400), 
                                   y=slope_bump_anti_steer_re * np.linspace(-25, 25, 400) + intercept_bump_anti_steer_re,
                                   mode='lines', name=f"y={slope_bump_anti_steer_re:.4f}x + {intercept_bump_anti_steer_re:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=2)
    fig_bump_anti_steer.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_anti_steer_re:.4f}x + {intercept_bump_anti_steer_re:.4f}",
            xref="x2", yref="y2",
            x=0, y=slope_bump_anti_steer_re * 0 + intercept_bump_anti_steer_re+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )
    
    # Left Camber plot
    fig_bump_anti_camber.add_trace(go.Scatter(x=df_bump_anti_offset['bump_anti_wheel_travel_li'], 
                                   y=df_bump_anti_offset['bump_anti_camber_li'],
                                   mode='lines+markers', name='Bump Anti-Phase Camber Left',
                                   line=dict(
                                        width=2,  # line width
                                        color='rgba(0, 0, 255, 1)'  # line color
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
    fig_bump_anti_camber.add_trace(go.Scatter(x=np.linspace(-25, 25, 400), 
                                   y=slope_bump_anti_camber_li * np.linspace(-25, 25, 400) + intercept_bump_anti_camber_li,
                                   mode='lines', name=f"y={slope_bump_anti_camber_li:.4f}x + {intercept_bump_anti_camber_li:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=1)
    fig_bump_anti_camber.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_anti_camber_li:.4f}x + {intercept_bump_anti_camber_li:.4f}",
            xref="x1", yref="y1",
            x=0, y=slope_bump_anti_camber_li * 0 + intercept_bump_anti_camber_li+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )

    # Right Camber plot
    fig_bump_anti_camber.add_trace(go.Scatter(x=df_bump_anti_offset['bump_anti_wheel_travel_re'], 
                                   y=df_bump_anti_offset['bump_anti_camber_re'],
                                   mode='lines+markers', name='Bump Anti-Phase Camber Right',
                                   line=dict(
                                        width=2,  # 设置线的宽度
                                        color='rgba(0, 0, 255, 1)'  # 设置线的颜色
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
    fig_bump_anti_camber.add_trace(go.Scatter(x=np.linspace(-25, 25, 400), 
                                   y=slope_bump_anti_camber_re * np.linspace(-25, 25, 400) + intercept_bump_anti_camber_re,
                                   mode='lines', name=f"y={slope_bump_anti_camber_re:.4f}x + {intercept_bump_anti_camber_re:.4f}",
                                   line=dict(color='red', width=3)), 
                        row=1, col=2)
    fig_bump_anti_camber.add_annotation(
        go.layout.Annotation(
            text=f"y = {slope_bump_anti_camber_re:.4f}x + {intercept_bump_anti_camber_re:.4f}",
            xref="x2", yref="y2",
            x=0, y=slope_bump_anti_camber_re * 0 + intercept_bump_anti_camber_re+0.5,  # Adjusting the y position a little above the regression line
            showarrow=False,
            font=dict(size=20, color='red')
        )
    )

    # Updating layout for titles, and legend for bump_anti Swheel rate plot
    fig_bump_anti_wheel_rate.update_layout(title_text="Steer Offset Plots", width=2400, height=1500,
                            xaxis_title="Rebound <<        RL wheel center vertical travel [mm]        >> Jounce",
                            yaxis_title="extension <<        RL vertical load [N]        >> compression",
                            xaxis2_title="Rebound <<        RR wheel center vertical travel [mm]        >> Jounce",
                            yaxis2_title="extension <<        RR vertical load [N]        >> compression",
                            showlegend=True)    
    
    
    # Updating layout for titles, and legend for bump_anti Steer plot
    fig_bump_anti_steer.update_layout(title_text="Steer Offset Plots", width=2400, height=1500,
                            xaxis_title="Rebound <<        RL wheel center vertical travel [mm]        >> Jounce",
                            yaxis_title="toe out <<        RL toe angle variation [deg]        >> toe in",
                            xaxis2_title="Rebound <<        RR wheel center vertical travel [mm]        >> Jounce",
                            yaxis2_title="toe out <<        RR toe angle variation [deg]        >> toe in",
                            showlegend=True)
    
    # Updating layout for titles, and legend for bump_anti Camber plot
    fig_bump_anti_camber.update_layout(title_text="Camber Offset Plots", width=2400, height=1500,
                             xaxis_title="Rebound <<        RL wheel center vertical travel [mm]        >> Jounce",
                             yaxis_title="top in <<        RL camber angle variation [deg]        >> top out",
                             xaxis2_title="Rebound <<        RR wheel center vertical travel [mm]        >> Jounce",
                             yaxis2_title="top in <<        RR camber angle variation [deg]        >> top out",
                             showlegend=True)
    
    
    
    
    
    
    # Update legend names for Steer plot
    for trace in fig_bump_anti_steer.data:
        if trace.name == 'Left Steer':
            trace.name = 'Left'
        elif trace.name == 'Right Steer':
            trace.name = 'Right'

    # Update legend names for Camber plot
    for trace in fig_bump_anti_camber.data:
        if trace.name == 'Left Camber':
            trace.name = 'Left'
        elif trace.name == 'Right Camber':
            trace.name = 'Right'
    
    return (
        fig_bump_anti_wheel_rate, fig_bump_anti_steer, fig_bump_anti_camber, 
        slope_bump_anti_wheel_rate_li, slope_bump_anti_wheel_rate_re, 
        slope_bump_anti_steer_li, slope_bump_anti_steer_re, 
        slope_bump_anti_camber_li, slope_bump_anti_camber_re, 
    )
    
    
#    return fig_bump_anti_wheel_rate, fig_bump_anti_steer, fig_bump_anti_camber, fig_bump_anti_wheel_base_change, fig_bump_anti_track_change, slope_li, slope_re, slope_camber_li, slope_camber_re

if __name__ == "__main__":
    main()
