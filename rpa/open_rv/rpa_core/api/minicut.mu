use glyph;
use gl;
use glu;
use gltext;
use gltexture;
use rvtypes;
use commands;
use image;
use math;

module: minicut
{
    global int texid;
    global string pattern;
    global float opacity;

    \: init (void; int w, int h,
             int tx, int ty,
             int tw, int th,
             bool stereo,
             bool rightEye,
             int frame,
             [string] argv)
    {
        string[] options = string[]();
        let _ : args = argv;
        while (args neq nil)
        {
            let input : rest = args;
            options.push_back(input);
            args = rest;
        }

        if (options.size() >= 1) pattern = options[0];
        if (options.size() >= 2) opacity = float(options[1]);
        else opacity = 1.0;
    }

    \: main (void; int w, int h,
             int tx, int ty,
             int tw, int th,
             bool stereo,
             bool rightEye,
             int frame,
             [string] argv)
    {
        string path = pattern % frame;

        // load and create texture for this frame
        let pixels = image(path);
        texid = createScalable2DTexture(pixels);

        // render the texture
        setupProjection(w, h);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

        drawTexture(texid, 0, 0, w, h, opacity, true);

        // clean up texture
        glDeleteTextures(int[](texid));
    }
}
