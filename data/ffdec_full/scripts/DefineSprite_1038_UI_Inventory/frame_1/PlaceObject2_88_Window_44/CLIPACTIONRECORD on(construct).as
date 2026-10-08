on(construct){
   while(true)
   {
      if(!(0x3B414126 & 0x3B414126))
      {
         if(!ord("\x07"))
         {
            break;
         }
      }
      else
      {
         §§push("\x16\x18\x14");
         §§push(false);
      }
      set(§§pop(),§§pop());
      §§push("contentPath");
      §§push("none");
      break;
   }
   set(§§pop(),§§pop());
   enabled = false;
   set("\x18\f\t",false);
   styleName = "LightBrownWindow";
   title = "";
}
