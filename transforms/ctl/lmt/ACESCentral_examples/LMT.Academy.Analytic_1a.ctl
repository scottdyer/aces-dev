import "ACESlib.Transform_Common";
import "ACESlib.LMT_Common";



const float SLOPE[3] = {0.85, 0.85, 0.85};
const float OFFSET[3] = {0.024, 0.024, 0.024};
const float POWER[3] = {0.9, 0.9, 0.9};
const float SAT = 0.94;



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

    aces = ASCCDL_inACEScct( aces, SLOPE, OFFSET, POWER, SAT);

    rOut = aces[0];
    gOut = aces[1];
    bOut = aces[2];
    aOut = aIn;
}