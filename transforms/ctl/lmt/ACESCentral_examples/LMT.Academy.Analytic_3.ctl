

// 
// Look Modification Transform
//
// Input is linear ACES2065-1
// Output is linear ACES2065-1
//


import "ACESlib.Transform_Common";
import "ACESlib.Utilities_Color";
import "ACESlib.RRT_Common";
import "ACESlib.LMT_Common";



// For the purposes of tuning, the hues are located at the following hue angles:
//   Y = 60
//   G = 120
//   C = 180
//   B = 240
//   M = 300
//   R = 360 / 0
void main 
(
    input varying float rIn, 
    input varying float gIn, 
    input varying float bIn, 
    input varying float aIn,
    output varying float rOut,
    output varying float gOut,
    output varying float bOut,
    output varying float aOut
)
{
    float aces[3] = {rIn, gIn, bIn};

    // Overall scale of C
    aces = scale_C( aces, 0.7);
        
    // Shift balance slightly yellow (add the "dingy-ness")
    float SLOPE[3] = {1.0, 1.0, 0.94};
    float OFFSET[3] = {0.0, 0.0, 0.02};
    float POWER[3] = {1.0, 1.0, 1.0};
    aces = ASCCDL_inACEScct( aces, SLOPE, OFFSET, POWER);

    // Boost contrast
    aces = gamma_adjust_linear( aces, 1.5, 0.18);

    // Rotate reds toward yellow
    aces = rotate_H_in_H( aces, 0., 30., 5.);

    // Rotate greens toward yellow
    aces = rotate_H_in_H( aces, 80., 60., -15.);

    // Rotate yellows toward red (more "golden")
    aces = rotate_H_in_H( aces, 52., 50., -14.);

    // Boost C in yellows
    aces = scale_C_at_H( aces, 45., 40., 1.4);

    // Rotate cyans toward blue
    aces = rotate_H_in_H( aces, 190., 40., 30.);

    // Boost C in blues
    aces = scale_C_at_H( aces, 240., 120., 1.4);
    
    rOut = aces[0];
    gOut = aces[1];
    bOut = aces[2];
    aOut = aIn;
}