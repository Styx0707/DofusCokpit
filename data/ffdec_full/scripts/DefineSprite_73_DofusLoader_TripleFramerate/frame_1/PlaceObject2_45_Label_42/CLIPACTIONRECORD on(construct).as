on(construct){
   while(true)
   {
      if(false)
      {
         if(!ord("\x05"))
         {
            break;
         }
      }
      else
      {
         §§push("\x07");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      enabled = true;
      html = false;
      multiline = false;
      styleName = "WhiteLeftMediumBoldLabel";
      text = "";
      §§push("wordWrap");
      §§push(false);
      if(!(getTimer() + 1))
      {
         §§goto(addr0d7c);
      }
      break;
   }
   set(§§pop(),§§pop());
   addr0d7c:
   §§pop()(§§pop());
}
