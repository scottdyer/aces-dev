
// <ACEStransformID>ACESlib.LMT_Common.a1.0.3</ACEStransformID>
// <ACESuserName>ACES 1.0 Lib - LMT Common</ACESuserName>

//
// Functions used in example LMTs
//



import "ACESlib.Utilities";




const float X_BRK = 0.0078125;
const float Y_BRK = 0.155251141552511;
const float A = 10.5402377416545;
const float B = 0.0729055341958355;

float lin_to_ACEScct( float in)
{
    if (in <= X_BRK)
        return A * in + B;
    else // (in > X_BRK)
        return (log2(in) + 9.72) / 17.52;
}

float ACEScct_to_lin( float in)
{
    if (in > Y_BRK)
        return pow( 2., in*17.52-9.72);
    else
        return (in - B) / A;
}

float[3] ACES_to_ACEScct( float in[3])
{
    // AP0 to AP1
    float ap1_lin[3] = mult_f3_f44( in, AP0_2_AP1_MAT);

    // Linear to ACEScct
    float acescct[3];
    acescct[0] = lin_to_ACEScct( ap1_lin[0]);
    acescct[1] = lin_to_ACEScct( ap1_lin[1]);
    acescct[2] = lin_to_ACEScct( ap1_lin[2]);
    
    return acescct;
}

float[3] ACEScct_to_ACES( float in[3])
{
    // ACEScct to linear
    float ap1_lin[3];
    ap1_lin[0] = ACEScct_to_lin( in[0]);
    ap1_lin[1] = ACEScct_to_lin( in[1]);
    ap1_lin[2] = ACEScct_to_lin( in[2]);

    // AP1 to AP0
    return mult_f3_f44( ap1_lin, AP1_2_AP0_MAT);
}

float[3] ASCCDL_inACEScct
(
    float acesIn[3], 
    uniform float SLOPE[3] = {1.0, 1.0, 1.0},
    uniform float OFFSET[3] = {0.0, 0.0, 0.0},
    uniform float POWER[3] = {1.0, 1.0, 1.0},
    uniform float SAT = 1.0
)
{
    // Convert ACES to ACEScct
    float acescct[3] = ACES_to_ACEScct( acesIn);

    // ASC CDL
    // Slope, Offset, Power
    acescct[0] = pow( clamp( (acescct[0] * SLOPE[0]) + OFFSET[0], 0., 1.), POWER[0]);
    acescct[1] = pow( clamp( (acescct[1] * SLOPE[1]) + OFFSET[1], 0., 1.), POWER[1]);
    acescct[2] = pow( clamp( (acescct[2] * SLOPE[2]) + OFFSET[2], 0., 1.), POWER[2]);
    
    // Saturation
    float luma = 0.2126*acescct[0] + 0.7152*acescct[1] + 0.0722*acescct[2];

    float satClamp = clamp( SAT, 0., HALF_POS_INF);    
    acescct[0] = luma + satClamp * (acescct[0] - luma);
    acescct[1] = luma + satClamp * (acescct[1] - luma);
    acescct[2] = luma + satClamp * (acescct[2] - luma);

    // Convert ACEScct to ACES
    return ACEScct_to_ACES( acescct);
}

float[3] gamma_adjust_linear( 
    float rgbIn[3], 
    uniform float GAMMA, 
    uniform float PIVOT = 0.18
)
{
    const float SCALAR = PIVOT / pow( PIVOT, GAMMA);

    float rgbOut[3] = rgbIn;
    if (rgbIn[0] > 0) rgbOut[0] = pow( rgbIn[0], GAMMA) * SCALAR;
    if (rgbIn[1] > 0) rgbOut[1] = pow( rgbIn[1], GAMMA) * SCALAR;
    if (rgbIn[2] > 0) rgbOut[2] = pow( rgbIn[2], GAMMA) * SCALAR;

    return rgbOut;
}


const float REC709_2_XYZ_MAT[4][4] = RGBtoXYZ( REC709_PRI, 1.0);    
const float REC709_RGB2Y[3] = { REC709_2_XYZ_MAT[0][1], 
                                REC709_2_XYZ_MAT[1][1], 
                                REC709_2_XYZ_MAT[2][1] };

float[3] sat_adjust(
    float rgbIn[3],
    uniform float SAT_FACTOR,
    uniform float RGB2Y[3] = REC709_RGB2Y
)
{
    const float SAT_MAT[3][3] = calc_sat_adjust_matrix( SAT_FACTOR, RGB2Y);    

    return mult_f3_f33( rgbIn, SAT_MAT);
}




// RGB / YAB / YCH conversion functions
// "YAB" is a geometric space of a unit cube rotated so its neutral axis run vertically
// "YCH" is a cylindrical representation of this, where C is the "chroma" and H is "hue"
// These are geometrically defined via ratios of RGB and are not intended to have any
// correlation to perceptual luminance, chrominance, or hue.

const float sqrt3over4 = 0.433012701892219;  // sqrt(3.)/4.
const float RGB_2_YAB_MAT[3][3] = {
  {1./3., 1./2., 0.0},
  {1./3., -1./4.,  sqrt3over4},
  {1./3., -1./4., -sqrt3over4}
};

float[3] rgb_2_yab( float rgb[3])
{
  float yab[3] = mult_f3_f33( rgb, RGB_2_YAB_MAT);

  return yab;
}

float[3] yab_2_rgb( float yab[3])
{
  float rgb[3] = mult_f3_f33( yab, invert_f33(RGB_2_YAB_MAT));

  return rgb;
}

float[3] yab_2_ych( float yab[3])
{
  float ych[3] = yab;

  ych[1] = sqrt( pow( yab[1], 2.) + pow( yab[2], 2.) );

  ych[2] = atan2( yab[2], yab[1] ) * (180.0 / M_PI);
  if (ych[2] < 0.0) ych[2] = ych[2] + 360.;

  return ych;
}

float[3] ych_2_yab( float ych[3] ) 
{
  float yab[3];
  yab[0] = ych[0];

  float h = ych[2] * (M_PI / 180.0);
  yab[1] = ych[1]*cos(h);
  yab[2] = ych[1]*sin(h);

  return yab;
}

float[3] rgb_2_ych( float rgb[3]) 
{
  return yab_2_ych( rgb_2_yab( rgb));
}

float[3] ych_2_rgb( float ych[3]) 
{
  return yab_2_rgb( ych_2_yab( ych));
}




// Regions of hue are targeted using a cubic basis shaper function. The controls for 
// the shape of this function are the center/peak (in degrees), and the full width 
// (in degrees) at the base. Values in the center of the function get 1.0 of an 
// adjustment while values at the tails of the function get 0.0 adjustment.
//
// For the purposes of tuning, the hues are located at the following hue angles:
//   Y = 60
//   G = 120
//   C = 180
//   B = 240
//   M = 300
//   R = 360 / 0
float[3] scale_C_at_H
( 
    float rgb[3], 
    float centerH,   // center of targeted hue region (in degrees)
    float widthH,    // full width at base of targeted hue region (in degrees)
    float percentC   // percentage of scale: 1.0 is no adjustment (i.e. 100%)
)
{
    float new_rgb[3] = rgb;
    
    float ych[3] = rgb_2_ych( rgb);

    if (ych[1] > 0.) {  // Only do the chroma adjustment if pixel is non-neutral

        float centeredHue = center_hue( ych[2], centerH);
        float f_H = cubic_basis_shaper( centeredHue, widthH);

        if (f_H > 0.0) {
            // Scale chroma in affected hue region
            float new_ych[3] = ych;
            new_ych[1] = ych[1] * (f_H * (percentC - 1.0) + 1.0);
            new_rgb = ych_2_rgb( new_ych);
        } else { 
            // If not in affected hue region, just return original values
            // This helps to avoid precision errors that can occur in the RGB->YCH->RGB 
            // conversion
            new_rgb = rgb; 
        }
    }

    return new_rgb;
}


// Regions of hue are targeted using a cubic basis shaper function. The controls for 
// the shape of this function are the center/peak (in degrees), and the full width 
// (in degrees) at the base. Values in the center of the function get 1.0 of an 
// adjustment while values at the tails of the function get 0.0 adjustment.
//
// For the purposes of tuning, the hues are located at the following hue angles:
//   Y = 60
//   G = 120
//   C = 180
//   B = 240
//   M = 300
//   R = 360 / 0
float[3] rotate_H_in_H
( 
    float rgb[3],
    float centerH,        // center of targeted hue region (in degrees)
    float widthH,         // full width at base of targeted hue region (in degrees)
    float degreesShift    // how many degrees (w/ sign) to rotate hue
)
{
    float ych[3] = rgb_2_ych( rgb);
    float new_ych[3] = ych;

    float centeredHue = center_hue( ych[2], centerH);
    float f_H = cubic_basis_shaper( centeredHue, widthH);

    float old_hue = centeredHue;
    float new_hue = centeredHue + degreesShift;
    float table[2][2] = { {0.0, old_hue}, 
                          {1.0, new_hue} };
    float blended_hue = interpolate1D( table, f_H);
        
    if (f_H > 0.0) new_ych[2] = uncenter_hue(blended_hue, centerH);
    
    return ych_2_rgb( new_ych);
}



float[3] scale_C( 
    float rgb[3], 
    float percentC      // < 1 is a decrease, 1.0 is unchanged, > 1 is an increase
)
{
    float ych[3] = rgb_2_ych( rgb);
    ych[1] = ych[1] * percentC;
    
    return ych_2_rgb( ych);
}