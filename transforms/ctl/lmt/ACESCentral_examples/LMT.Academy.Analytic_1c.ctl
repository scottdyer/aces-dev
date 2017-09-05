import "ACESlib.Transform_Common";
import "ACESlib.LMT_Common";



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

    // Adjust contrast
    const float GAMMA = 0.6;
    aces = gamma_adjust_linear( aces, GAMMA);
    
    // Adjust saturation
    const float SAT_FACTOR = 0.85;
    aces = sat_adjust( aces, SAT_FACTOR);
    
    rOut = aces[0];
    gOut = aces[1];
    bOut = aces[2];
    aOut = aIn;
}