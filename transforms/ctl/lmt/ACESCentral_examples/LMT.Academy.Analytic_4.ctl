// "Bleach bypass" look


import "ACESlib.Transform_Common";
import "ACESlib.Utilities_Color";
import "ACESlib.RRT_Common";
import "ACESlib.LMT_Common";



float[3] overlay_f3( float a[3], float b[3])
{
    const float LUMA_CUT = lin_to_ACEScct( 0.5); 
    // 0.5 seems to work well (i.e. scene exposures at 50% reflectance). 
    // Other values were tried (e.g. 0.18, etc.) and can be used, if desired.

    float luma = 0.2126*a[0] + 0.7152*a[1] + 0.0722*a[2];
    // Simple luma weighting copied from the ASC CDL definition.

    float out[3];
    if (luma < LUMA_CUT) {
        out[0] = 2.*a[0]*b[0];
        out[1] = 2.*a[1]*b[1];
        out[2] = 2.*a[2]*b[2];
    } else {
        out[0] = 1.-(2.*(1.-a[0])*(1.-b[0]));
        out[1] = 1.-(2.*(1.-a[1])*(1.-b[1]));
        out[2] = 1.-(2.*(1.-a[2])*(1.-b[2]));
    }

    return out;
}



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
    
    // -- Node 1 --
    // Lower saturation slightly
    float a[3] = sat_adjust( aces, 0.9);    // 0.9 worked well for the images I used
    // Boost exposure 
    a = mult_f_f3( 2.0, a);     // 2.0 seemed to work well to prevent blended image 
                                // from appearing too dark

    // -- Node 2 --
    // Desaturate
    float b[3] = sat_adjust( aces, 0.0);  // 0.0 leads to no saturation
    // Increase contrast
    b = gamma_adjust_linear( b, 1.2);     // 1.2 increases image contrast around mid-gray

    // Data is linear up to this point, so exposure adjustment can be achieved via a 
    // scale factor (multiplication) and contrast can be adjusted with a gamma factor.
    
    
    // Blend with "overlay" mode
    // First convert ACES2065-1 to ACEScct
    a = ACES_to_ACEScct( a);
    b = ACES_to_ACEScct( b);
    
    float blend[3];
    blend = overlay_f3( a, b);

    // Convert back to ACES2065-1
    float out[3] = ACEScct_to_ACES( blend);
    rOut = out[0];
    gOut = out[1];
    bOut = out[2];
    aOut = aIn;
}