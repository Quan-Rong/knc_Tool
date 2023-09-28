import streamlit as st
from PIL import Image


st.set_page_config(
    page_title="Hello",
    page_icon="👋", layout="wide"
)

st.write('''# &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; K&C Results Post-Processing for G-Rear Suspension Development 👋
         ''')

main_image=Image.open('logo_main_01.JPG')
st.image(main_image, caption='Version: Beta V0.2', use_column_width='always')

st.sidebar.success("Select a locacase above.")

st.markdown('''---''')

st.markdown(
    """
    an open-source app framework built specifically for
    Gestamp new rear suspension development projects.
    **👈 Select a loadcase from the sidebar** to build the results report!
        
    ### Update Beta V0.2
    - Update curve fitting based on PE documentation [Github.com](https://github.com/)
    - Update documentation [documentation](https://github.com/)
    - Update Getamp K&C Database
    - Getamp K&C Database (new vehicle ID.4x, Tesla Model Y 2022 (mod. Spring Version) on ABD)
        
        
    ### Current existing bugs   
    * Due to configuration issues, the remote Amazon (AWS) host cannot read the main program data from Github. Temporarily switch the Cloud deployment to local deployment.
    * Some K&C results have not been processed yet.
    * After the "Statistic Results Show" button is activated, there is a repeated invocation, causing data overflow. The feature has been temporarily disabled. 
          
    ### See more complex demos
    - Use K&C Results Post-Processing Tool to [analyze the Adams/Car K&C Results](https://github.com/)
"""
)

st.markdown('''---''')

def main():
    cs_body()
    
def cs_body():

    col1, col2, col3 = st.columns(3)

    #######################################
    # COLUMN 1
    #######################################
    
    # Display text

    col1.subheader('Kinematic - Bump Test')
    col1.code('''
>>>01. 'Wheel Rate'
>>>02. 'Wheel Rate Slope'
>>>03. 'Ride Rate'
>>>04. 'Tire Radial Rate Slope'
>>>05. 'Bump Steer'
>>>06. 'Bump Camber'
>>>07. 'Toe Change @WC '
>>>08. 'Toe Change @CP'
>>>09. 'Wheel Recession'
>>>10. 'Toe Angle Change @Bump 50mm'
>>>11. 'Toe Angle Change @Rebound 50mm'
>>>12. 'Wheel Travel @2g Half Load'
>>>13. 'Wheel Rate @2g Half Load'
>>>14. 'Side View Swing Arm Angle'
>>>15. 'Side View Swing Arm Length'
>>>16. 'Roll Rate @WC'
>>>17. 'Total Roll Rate'
>>>18. 'Kinematic Roll Center Height'
    ''')
    
    # Display interactive widgets

    col1.subheader('Compliance - Lateral Force Test')
    col1.code('''
>>>01. 'LatForce Steer'
>>>02. 'LatForce Steer Slope'
>>>03. 'LatForce Camber'
>>>04. 'LatForce Compliance @WC'
>>>05. 'LatForce Compliance @CP with Tire'
>>>06. 'LatForce Compliance @CP'
>>>07. 'Compliance Roll Center Height'
    ''')    


    #######################################
    # COLUMN 2
    #######################################

    # Display interactive widgets

    col2.subheader('Kinematic - Roll Test')
    col2.code('''
>>>01. 'Wheel Rate'
>>>02. 'Wheel Rate Slope'
>>>03. 'Roll Rate @WC'
>>>04. 'Total Roll Rate'
>>>05. 'Toe Change @WC'
>>>06. 'Toe Change @CP'
>>>07. 'Roll Camber'
>>>08. 'Roll Camber Relative Ground'
>>>09. 'out-of-Phase Bump Steer'
>>>10. 'Out-of-Phase Bump Camber'
>>>11. 'Kinematic Roll Center Height'
# * optional kwarg unsafe_allow_html = True

    ''')
   

    # Display data

    col2.subheader('Compliance - Acceleration Test')
    col2.code('''
>>>01. 'Drive Steer'
>>>02. 'Drive Wheel Recession'
>>>03. 'Drive Anti Lift Angle'
    ''')

    # Display data

    col2.subheader('Compliance - Align Torque Test')
    col2.code('''
>>>01. 'AligTorque Steer'
>>>02. 'AligTorque Slope'
>>>03. 'Align Torque Camber'
    ''')



    #######################################
    # COLUMN 3
    #######################################


    # Connect to data sources
    
    col3.subheader('Kinematic - Steering')

    col3.code('''
>>>01. 'Kingpin Caster Angle'
>>>02. 'Kingpin Caster Angle'
>>>03. 'Kingpin Inclination Angle'
>>>04. 'Scrub Radius'
>>>05. 'Caster Moment Arm'
>>>06. 'Spindle Length'
>>>07. 'Caster Offset'
>>>08. 'Steer Ratio'
>>>09. 'Steer Ratio Fluctuation'
>>>10. 'Steer Ratio Slope'
>>>11. 'Steer Friction'
>>>12. 'Steer Backlash'
>>>13. 'Percent Ackerman'
>>>14. 'Ackerman Error'
>>>15. 'Max Steer Angle'
>>>16. 'Steer Wheel Circle'
              ''')


    # Optimize performance

    col3.subheader('Compliance - Braking Test')
    col3.code('''
>>>01. 'Brake Steer'
>>>02. 'Brake Camber'
>>>03. 'Brake Wheel Recession'
>>>04. 'Brake @CP Recession'
>>>05. 'Brake Anti-Dive Angle'
>>>06. 'Brake Dive'
    ''')




    return None

# Run main()

if __name__ == '__main__':
    main()